
import multiprocessing

cpu_cores = multiprocessing.cpu_count()
threads = str(cpu_cores * 2)


class SubdomainScanning:
    reports = [
        {
            "path": "$WORKSPACE/subdomain/final-$OUTPUT.txt",
            "type": "bash",
            "note": "final, slack, diff",
        }
    ]
    logs = []
    commands = {
        'general': [
            {
                "banner": "Amass",
                "cmd": "$GO_PATH/amass enum -timeout 10 -active -max-dns-queries 10000 -dir $WORKSPACE/subdomain/amass-$OUTPUT -d $TARGET -o $WORKSPACE/subdomain/$OUTPUT-amass.txt",
                "output_path": "$WORKSPACE/subdomain/$OUTPUT-amass.txt",
                "std_path": "$WORKSPACE/subdomain/std-$TARGET-amass.std"
            },
            {
                "banner": "Subfinder",
                "cmd": "$GO_PATH/subfinder -d $TARGET -t 100 -o $WORKSPACE/subdomain/$OUTPUT-subfinder.txt -nW",
                "output_path": "$WORKSPACE/subdomain/$OUTPUT-subfinder.txt",
                "std_path": "$WORKSPACE/subdomain/std-$TARGET-subfinder.std"
            },
            {
                "banner": "chaos",
                "cmd": "ssh 'port@last-one.duckdns.org' -o 'StrictHostKeyChecking no' -o ServerAliveInterval=60 -i '/tmp/516.pem' -f \"find /root/chaos/ -type f -name '$TARGET*'\" | xargs -I % rsync --protect-args -avz -e 'ssh -i /tmp/516.pem' 'port@last-one.duckdns.org:%' '$WORKSPACE/subdomain/' && cat $WORKSPACE/subdomain/$TARGET.txt_* | sort -u -o $WORKSPACE/subdomain/chaos-$TARGET.txt",
                "output_path": "$WORKSPACE/subdomain/chaos-$TARGET.txt"
            },
            {
                "banner": "subx",
                "cmd": "python3 /root/get_subx.py -d $TARGET -o $WORKSPACE/subdomain/$OUTPUT-subx.txt",
                "output_path": "$WORKSPACE/subdomain/$OUTPUT-subx.txt",
                "std_path": "$WORKSPACE/subdomain/std-$TARGET-subx.std"
            },
            {
                "banner": "rusolver",
                "cmd": "cat /root/all.txt | /root/rusolver -q -d $OUTPUT -t 5000 | tee $WORKSPACE/subdomain/$OUTPUT-rusolver.txt",
                "output_path": "$WORKSPACE/subdomain/$OUTPUT-rusolver.txt",
                "std_path": "$WORKSPACE/subdomain/std-$TARGET-rusolver.std"
            },
            {
                "banner": "assetfinder",
                "cmd": "$GO_PATH/assetfinder -subs-only $TARGET | tee $WORKSPACE/subdomain/$OUTPUT-assetfinder.txt",
                "output_path": "$WORKSPACE/subdomain/$OUTPUT-assetfinder.txt",
                "std_path": "$WORKSPACE/subdomain/std-$TARGET-assetfinder.std"
            },
            {
                "banner": "findomain",
                "cmd": "$PLUGINS_PATH/findomain -u $WORKSPACE/subdomain/$OUTPUT-findomain.txt -t $TARGET ",
                "output_path": "$WORKSPACE/subdomain/$TARGET-findomain.txt",
                "std_path": "$WORKSPACE/subdomain/std-$TARGET-findomain.std",
            },
        ],
        'slow': [
            {
                "banner": "massdns",
                "cmd": "$PLUGINS_PATH/massdns/scripts/subbrute.py /root/all.txt $TARGET | $PLUGINS_PATH/massdns/bin/massdns -r /root/resolvers.txt -q -t A -o S -w $WORKSPACE/subdomain/raw-massdns.txt",
                "output_path": "$WORKSPACE/subdomain/raw-massdns.txt",
                "std_path": "$WORKSPACE/subdomain/std-raw-massdns.txt",
                "post_run": "clean_massdns",
                "cleaned_output": "$WORKSPACE/subdomain/$OUTPUT-massdns.txt",
            },

        ],
    }


class VhostScan:
    note = "Pro-only"
    reports = [
        {
            "path": "$WORKSPACE/vhosts/vhost-$OUTPUT.txt",
            "type": "bash",
            "note": "final",
        }
    ]
    logs = []
    commands = {
        'general': [
            {
                "banner": "Gobuster Vhost",
                "cmd": "$ALIAS_PATH/vhosts -i '[[0]]' -o '$WORKSPACE/vhosts/raw/' -s '$WORKSPACE/vhosts/raw-summary-$OUTPUT.txt' -p '$PLUGINS_PATH' -w $DATA_PATH/wordlists/dns/virtual-host-scanning.txt",
                "output_path": "",
                "std_path": "",
                "chunk": 5,
                "cmd_type": "list",
                "resources": "l0|$WORKSPACE/subdomain/final-$OUTPUT.txt",
                "post_run": "clean_multi_gobuster",
                "cleaned_output": "$WORKSPACE/vhosts/vhosts-$OUTPUT.txt",
            },
        ],
    }


class PermutationScan:
    note = "Pro-only"
    reports = [
        {
            "path": "$WORKSPACE/permutation/permutation-$OUTPUT.txt",
            "type": "bash",
            "note": "final",
        }
    ]
    logs = []
    commands = {
        'general': [
            {
                "banner": "goaltdns",
                "cmd": "$GO_PATH/goaltdns -w $DATA_PATH/wordlists/dns/short-permutation.txt -l $WORKSPACE/subdomain/final-$OUTPUT.txt -o $WORKSPACE/permutation/permutation-$OUTPUT.txt",
                "output_path": "$WORKSPACE/permutation/permutation-$OUTPUT.txt",
                "std_path": "",
            },
        ],
    }


class Probing:
    reports = [
        {
            "path": "$WORKSPACE/probing/ip-$OUTPUT.txt",
            "type": "bash",
            "note": "final, slack, diff",
        },
        {
            "path": "$WORKSPACE/probing/raw-allmassdns.txt",
            "type": "bash",
            "note": "final",
        },
        {
            "path": "$WORKSPACE/probing/resolved-$OUTPUT.txt",
            "type": "bash",
            "note": "final, diff",
        },
        {
            "path": "$WORKSPACE/probing/http-$OUTPUT.txt",
            "type": "bash",
            "note": "final, slack, diff",
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                # this only run if something wrong with custom resolvers
                "banner": "massdns resolve IP",
                "requirement": "$WORKSPACE/probing/raw-all-$OUTPUT.txt",
                "cmd": "cat $WORKSPACE/probing/raw-all-$OUTPUT.txt | $PLUGINS_PATH/massdns/bin/massdns -r $DATA_PATH/resolvers.txt -q -t A -o S -w $WORKSPACE/probing/raw-allmassdns.txt",
                "output_path": "$WORKSPACE/probing/raw-allmassdns.txt",
                "std_path": "",
                "waiting": "first",
                "pre_run": "get_subdomains",
                "post_run": "clean_massdns",
                "cleaned_output": "$WORKSPACE/probing/ip-$OUTPUT.txt",
            },
            {
                "banner": "httpx",
                "requirement": "$WORKSPACE/probing/resolved-$OUTPUT.txt",
                "cmd": "/usr/local/bin/httpx -l $WORKSPACE/probing/resolved-$OUTPUT.txt -timeout 2 -ports 80,81,8080,8081,8005,8009,443,9090,9000,8000,488,8008,8009,5222,8444,8010,8880,8118,8123,5000,4000,3000,5432,8090,8005 -silent -o $WORKSPACE/probing/http-$OUTPUT.txt && sed -i -e 's/:80$//g' $WORKSPACE/probing/http-$OUTPUT.txt && sed -i -e 's/:443$//g' $WORKSPACE/probing/http-$OUTPUT.txt && cat $WORKSPACE/probing/http-$OUTPUT.txt | grep 'https' | xargs -I % echo % | sed 's/https/http/' | sed 's/8443/8080/' | sed 's/http:\/\///' | xargs -I {} sed --in-place '/http:\/\/{}/d' $WORKSPACE/probing/http-$OUTPUT.txt",
                "output_path": "$WORKSPACE/probing/http-$OUTPUT.txt",
                "std_path": "$WORKSPACE/probing/std-http-$OUTPUT.std",
                #"post_run": "get_domain",
            },
            {
                "banner": "naabu",
                "requirement": "$WORKSPACE/probing/resolved-$OUTPUT.txt",
                "cmd": "cat $WORKSPACE/probing/resolved-$OUTPUT.txt | /root/cf-check -d | /root/naabu -retries 1 -rate 1000 -exclude-cdn -top-ports 200 -silent -o $WORKSPACE/probing/naabu-$OUTPUT.txt && sed -i -e 's/.*:80$//g' $WORKSPACE/probing/naabu-$OUTPUT.txt && sed -i -e 's/.*:443$//g' $WORKSPACE/probing/naabu-$OUTPUT.txt && sed -i '/^[[:space:]]*$/d' $WORKSPACE/probing/naabu-$OUTPUT.txt",
                "output_path": "$WORKSPACE/probing/naabu-$OUTPUT.txt",
                "std_path": "$WORKSPACE/probing/std-naabu-$OUTPUT.std",
                "waiting": "last"
            }
        ],
    }


class Formatting:
    reports = [
        {
            "path": "$WORKSPACE/formatted/$OUTPUT-domains.txt",
            "type": "bash",
            "note": "final, slack"
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                "requirement": "$WORKSPACE/probing/domains-$OUTPUT.txt",
                "banner": "Formatting Input",
                "cmd": "$ALIAS_PATH/format_input -i $WORKSPACE/probing/domains-$OUTPUT.txt -o '$WORKSPACE/formatted/$OUTPUT'",
                "output_path": "$WORKSPACE/formatted/$OUTPUT-domains.txt",
                "std_path": "",
                "waiting": "first",
            },
        ],
    }


class CORScan:
    reports = [
        {
            "path": "$WORKSPACE/cors/$OUTPUT-corstest.txt",
            "type": "bash",
            "note": "final",
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                "requirement": "$WORKSPACE/probing/http-$OUTPUT.txt",
                "banner": "CORS Scan",
                "cmd": "python2 $PLUGINS_PATH/CORStest/corstest.py -p 50 $WORKSPACE/probing/http-$OUTPUT.txt | tee $WORKSPACE/cors/$OUTPUT-corstest.txt",
                "output_path": "$WORKSPACE/cors/$TARGET-corstest.txt",
                "std_path": "$WORKSPACE/cors/std-$TARGET-corstest.std",
            }
        ],
    }


class Fingerprint:
    reports = [
        {
            "path": "$WORKSPACE/fingerprint/$OUTPUT-technology.json",
            "type": "bash",
            "note": "final",
        }
    ]
    logs = []
    commands = {
        'general': [
            {
                "banner": "webanalyze",
                "cmd": f"$GO_PATH/webanalyze -apps $DATA_PATH/apps.json -hosts $WORKSPACE/probing/http-$OUTPUT.txt -output json -worker {threads} | tee $WORKSPACE/fingerprint/$OUTPUT-technology.json",
                "output_path": "$WORKSPACE/fingerprint/$OUTPUT-technology.json",
                "std_path": "$WORKSPACE/fingerprint/std-$OUTPUT-technology.std",
                "post_run": "update_tech",
                "cleaned_output": "$WORKSPACE/fingerprint/formatted-tech-$OUTPUT.txt",
            },
            {
                "banner": "meg /",
                "cmd": "$GO_PATH/meg / $WORKSPACE/probing/http-$OUTPUT.txt $WORKSPACE/fingerprint/responses/ -v -c 100",
                "output_path": "$WORKSPACE/fingerprint/responses/index",
                "std_path": "",
            },
        ],
    }


class ScreenShot:
    reports = [
        {
            "path": "$WORKSPACE/screenshot/$OUTPUT-aquatone/aquatone_report.html",
            "type": "html",
            "note": "final",
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                "banner": "aquatone",
                "cmd": f"cat $WORKSPACE/probing/resolved-$OUTPUT.txt | /root/aquatone -scan-timeout 1000 -threads {threads} -out $WORKSPACE/screenshot/$OUTPUT-aquatone",
                "output_path": "$WORKSPACE/screenshot/$OUTPUT-aquatone/aquatone_report.html",
                "std_path": "$WORKSPACE/screenshot/std-$OUTPUT-aquatone.std"
            },
        ],
    }


class StoScan:
    reports = [
        {
            "path": "$WORKSPACE/stoscan/takeover-$TARGET-tko-subs.txt",
            "type": "bash",
            "note": "final"
        },
        {
            "path": "$WORKSPACE/stoscan/takeover-$TARGET-subjack.txt",
            "type": "bash"
        },
        {
            "path": "$WORKSPACE/stoscan/all-dig-info.txt",
            "type": "bash"
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                "banner": "tko-subs",
                "cmd": "$GO_PATH/tko-subs -data $DATA_PATH/providers-data.csv -domains $WORKSPACE/probing/resolved-$OUTPUT.txt -output $WORKSPACE/stoscan/takeover-$TARGET-tko-subs.txt",
                "output_path": "$WORKSPACE/stoscan/takeover-$TARGET-tko-subs.txt",
                "std_path": "$WORKSPACE/stoscan/std-takeover-$TARGET-tko-subs.std",
            },
            {
                "banner": "Subjack",
                "cmd": "$GO_PATH/subjack -v -m -c $DATA_PATH/fingerprints.json -w $WORKSPACE/probing/resolved-$OUTPUT.txt -t 100 -timeout 30 -o $WORKSPACE/stoscan/takeover-$TARGET-subjack.txt -ssl",
                "output_path": "$WORKSPACE/stoscan/takeover-$TARGET-subjack.txt",
                "std_path": "$WORKSPACE/stoscan/std-takeover-$TARGET-subjack.std"
            },
            {
                "banner": "subzy",
                "cmd": "$GO_PATH/subzy -hide_fails -https -concurrency 20 -targets $WORKSPACE/probing/resolved-$OUTPUT.txt | tee $WORKSPACE/stoscan/takeover-$TARGET-subzy.txt",
                "output_path": "$WORKSPACE/stoscan/takeover-$TARGET-subzy.txt",
                "std_path": "$WORKSPACE/stoscan/std-takeover-$TARGET-subzy.std"
            },
            {
                "banner": "massdns resolve IP",
                "cmd": "cat $WORKSPACE/probing/resolved-$OUTPUT.txt | $PLUGINS_PATH/massdns/bin/massdns -r $PLUGINS_PATH/massdns/lists/resolvers.txt -q -t A -o F -w $WORKSPACE/stoscan/all-dig-info.txt",
                "output_path": "$WORKSPACE/stoscan/all-dig-info.txt",
                "std_path": "",
                "waiting": "first",
            },
        ],
    }


class LinkFinding:
    reports = [
        {
            "path": "$WORKSPACE/links/summary-$OUTPUT.txt",
            "type": "bash",
            "note": "final",
        },
        {
            "path": "$WORKSPACE/links/raw-wayback-$OUTPUT.txt",
            "type": "bash",
            "note": "final",
        }
    ]
    logs = []
    commands = {
        'general': [
            {
                "requirement": "$WORKSPACE/probing/resolved-$OUTPUT.txt",
                "banner": "waybackurls",
                "cmd": "cat $WORKSPACE/probing/resolved-$OUTPUT.txt | /root/go/bin/waybackurls | egrep -v '(.ico|.woff|.eot|.ttf|.woff2|.fonts|.font|.css|.png|.jpeg|.jpg|.svg|.gif|.wolf)' | tee $WORKSPACE/links/raw-wayback-$OUTPUT.txt ",
                "output_path": "$WORKSPACE/links/raw-wayback-$OUTPUT.txt",
                "std_path": "$WORKSPACE/links/std-wayback-$OUTPUT.std",
                "post_run": "clean_waybackurls",
                "cleaned_output": "$WORKSPACE/links/waybackurls-$OUTPUT.txt",
            },
            {
                "requirement": "$WORKSPACE/probing/http-$OUTPUT.txt",
                "banner": "ZAP Crawler",
                "cmd": "python3 /root/zap.py $OUTPUT",
                "output_path": "$WORKSPACE/links/zap_result.txt",
            },
            {
                "requirement": "$WORKSPACE/links/raw-wayback-$OUTPUT.txt",
                "banner": "Formatting Input",
                "cmd": "cat $WORKSPACE/links/raw-wayback-$OUTPUT.txt $WORKSPACE/links/zap_result.txt | grep -v '/robots.txt' | grep -v '/sitemap.xml' | /root/go/bin/qsreplace -a | httpx -no-color -status-code -threads 200 -silent | grep -v 404 | tee $WORKSPACE/links/status-$OUTPUT.txt | grep -E '^200' | cut -d ' ' -f 1 | tee $WORKSPACE/links/ok-http.txt | grep -E '\.js' | tee $WORKSPACE/links/js_links.txt && grep -v '\.js' $WORKSPACE/links/ok-http.txt | tee $WORKSPACE/links/no-js.txt && grep -E '^403' $WORKSPACE/links/status-$OUTPUT.txt | cut -d ' ' -f 1 | tee $WORKSPACE/links/403-http.txt",
                "output_path": "$WORKSPACE/links/status-$OUTPUT.txt",
                "std_path": "$WORKSPACE/links/status-$OUTPUT.std",
                "waiting": "last",
            },
        ],
    }


class PortScan:
    reports = [
        {
            "path": "$WORKSPACE/portscan/final-$OUTPUT.html",
            "type": "html",
            "note": "final",
        },
        {
            "path": "$WORKSPACE/portscan/$OUTPUT.html",
            "type": "html",
            "note": "final",
        },
        {
            "path": "$WORKSPACE/portscan/beautify-$OUTPUT.txt",
            "type": "bash",
            "note": "final, slack, diff",
        },
        {
            "path": "$WORKSPACE/portscan/$OUTPUT-aquatone/aquatone_report.html",
            "type": "html",
            "note": "final",
        },
        {
            "path": "$WORKSPACE/portscan/screenshot/$OUTPUT-raw-gowitness.html",
            "type": "html",
            "note": "final",
        },
        {
            "path": "$WORKSPACE/portscan/screenshot/$OUTPUT-raw-gowitness.html",
            "type": "html",
            "note": "",
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                # "requirement": "$WORKSPACE/formatted/ip-$OUTPUT.txt",
                "banner": "Masscan 65535 ports",
                "cmd": "$ALIAS_PATH/portscan -i $TARGET -o '$WORKSPACE/portscan/$OUTPUT' -s '$WORKSPACE/portscan/summary.txt' -p '$PLUGINS_PATH'",
                "output_path": "$WORKSPACE/portscan/$OUTPUT.xml",
                "std_path": "",
                "waiting": "first",
            },
            {
                "requirement": "$WORKSPACE/portscan/$OUTPUT.csv",
                "banner": "CSV beautify",
                "cmd": "cat $WORKSPACE/portscan/$OUTPUT.csv | csvlook --no-inference | tee $WORKSPACE/portscan/beautify-$OUTPUT.txt",
                "output_path": "$WORKSPACE/portscan/beautify-$OUTPUT.txt",
                "std_path": "",
                "pre_run": "update_ports",
                "cleaned_output": "$WORKSPACE/portscan/formatted-$OUTPUT.txt",
            },
            {
                "requirement": "$WORKSPACE/portscan/$OUTPUT.csv",
                "banner": "Httprode new port",
                "cmd": '''cat $WORKSPACE/portscan/$OUTPUT.csv | awk -F',' '{print $1":"$4}' | httprobe -c 30 | tee $WORKSPACE/portscan/http-$OUTPUT.txt''',
                "output_path": "$WORKSPACE/portscan/http-$OUTPUT.txt",
                "std_path": "",
            },
            {
                "requirement": "$WORKSPACE/portscan/http-$OUTPUT.txt",
                "banner": "aquatone",
                "cmd": f"cat $WORKSPACE/portscan/http-$OUTPUT.txt | /root/aquatone -screenshot-timeout 50000 -threads {threads} -out $WORKSPACE/portscan/$OUTPUT-aquatone",
                "output_path": "$WORKSPACE/portscan/$OUTPUT-aquatone/aquatone_report.html",
                "std_path": "$WORKSPACE/portscan/std-$OUTPUT-aquatone.std",
                "waiting": "last",
            },

            # {
            #     "requirement": "$WORKSPACE/portscan/$OUTPUT.csv",
            #     "banner": "Screenshot on ports found",
            #     "cmd": "$GO_PATH/gowitness file -s $WORKSPACE/portscan/scheme-$OUTPUT.txt -t 30 --log-level fatal --destination $WORKSPACE/portscan/screenshot/raw-gowitness/ --db $WORKSPACE/portscan/screenshot/gowitness.db",
            #     "output_path": "$WORKSPACE/portscan/screenshot/gowitness.db",
            #     "std_path": "",
            #     "post_run": "clean_gowitness",
            #     "pre_run": "get_scheme",
            #     "cleaned_output": "$WORKSPACE/portscan/screenshot-$OUTPUT.html",
            #     "waiting": "last",
            # },
            
        ],
    }


class VulnScan:
    reports = [
        {
            "path": "$WORKSPACE/vulnscan/final-$OUTPUT.html",
            "type": "html",
            "note": "final",
        },
        {
            "path": "$WORKSPACE/vulnscan/beautify-summary-$OUTPUT.txt",
            "type": "bash",
            "note": "final",
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                # "requirement": "$TARGET",
                "banner": "Nmap all port",
                "cmd": "$ALIAS_PATH/vulnscan -i $TARGET -o '$WORKSPACE/vulnscan/details/$OUTPUT' -s '$WORKSPACE/vulnscan/summary-$OUTPUT.csv' -p '$PLUGINS_PATH'",
                "output_path": "$WORKSPACE/vulnscan/details/$OUTPUT.gnmap",
                "std_path": "$WORKSPACE/vulnscan/details/std-$OUTPUT.std",
                "chunk": 3,
                "post_run": "gen_summary",
                "waiting": "first",
            },
            {
                "requirement": "$WORKSPACE/vulnscan/summary-$OUTPUT.csv",
                "banner": "CSV beautify",
                "cmd": "cat $WORKSPACE/vulnscan/summary-$OUTPUT.csv | csvlook --no-inference | tee $WORKSPACE/vulnscan/beautify-summary-$OUTPUT.txt",
                "output_path": "$WORKSPACE/vulnscan/beautify-summary-$OUTPUT.txt",
                "std_path": "",
            },
            {
                "requirement": "$WORKSPACE/vulnscan/summary-$OUTPUT.csv",
                "banner": "Screenshot on ports found",
                "cmd": "$GO_PATH/gowitness file -s $WORKSPACE/vulnscan/scheme-$OUTPUT.txt -t 30 --log-level fatal --destination  $WORKSPACE/vulnscan/screenshot/raw-gowitness/ --db $WORKSPACE/vulnscan/screenshot/gowitness.db",
                "output_path": "$WORKSPACE/vulnscan/screenshot/gowitness.db",
                "std_path": "",
                # "waiting": "last",
                "post_run": "clean_gowitness",
                "pre_run": "get_scheme",
            },
        ],
    }


class IPSpace:
    reports = [
        {
            "path": "$WORKSPACE/ipspace/summary-$OUTPUT.txt",
            "type": "bash",
            "note": "final",
        },
        {
            "path": "$WORKSPACE/ipspace/range-$OUTPUT.txt",
            "type": "bash",
            "note": "final",
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                "banner": "Metabigor IP Lookup",
                "cmd": "echo '$TARGET' | $GO_PATH/metabigor net -o $WORKSPACE/ipspace/range-$OUTPUT.txt",
                "output_path": "$WORKSPACE/ipspace/range-$OUTPUT.txt",
                "std_path": "",
                "post_run": "get_amass",
                "cleaned_output": "$WORKSPACE/ipspace/summary-$OUTPUT.txt",
            },
        ],
    }


class DirbScan:
    reports = [
        {
            "path": "$WORKSPACE/directory/raw-summary.txt",
            "type": "bash",
            "note": "final, diff, slack",
        },
        {
            "path": "$WORKSPACE/directory/beautify-summary.csv",
            "type": "bash",
            "note": "final, diff, slack",
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                "requirement": "$WORKSPACE/formatted/$OUTPUT-paths.txt",
                "banner": "Format fuzz URL",
                "cmd": "cat $WORKSPACE/formatted/$OUTPUT-paths.txt | unfurl -u format %s://%d%p/FUZZ | grep -v 'http:///FUZZ' > $WORKSPACE/directory/fuzz-$OUTPUT.txt",
                "output_path": "$WORKSPACE/directory/fuzz-$OUTPUT.txt",
                "std_path": "",
                "waiting": "first",
            },
            {
                "banner": "ffuf dirscan",
                "cmd": "$ALIAS_PATH/dirscan -i [[0]] -w '$DATA_PATH/wordlists/content/quick.txt' -o '$WORKSPACE/directory/raw' -p '$GO_PATH' -s '$WORKSPACE/directory'",
                "output_path": "",
                "std_path": "",
                "chunk": 5,
                "cmd_type": "list",
                "resources": "l0|$WORKSPACE/directory/fuzz-$OUTPUT.txt",
            },
            {
                "banner": "csv beautify",
                "cmd": "cat $WORKSPACE/directory/raw/* | csvcut -c 2-6 | csvlook | tee -a $WORKSPACE/directory/beautify-summary.csv",
                "output_path": "",
                "std_path": "",
                "waiting": "last",
            },
        ],
    }



class GitScan:
    reports = [
        {
            "path": "$WORKSPACE/gitscan/$OUTPUT-user.txt",
            "type": "bash",
        },
        {
            "path": "$WORKSPACE/gitscan/$TARGET-gitrob.txt",
            "type": "bash",
        },
    ]
    logs = []
    commands = {
        'general': [
            {
                "banner": "parse input",
                "cmd": "$ALIAS_PATH/git_format -i '$RAW_TARGET' -o '$WORKSPACE/gitscan/$OUTPUT'",
                "output_path": "$WORKSPACE/gitscan/$OUTPUT-user.txt",
                "std_path": "",
                "waiting": "first",
            },
            {
                "requirement": "$WORKSPACE/gitscan/$OUTPUT-repo.txt",
                "banner": "Git recon repo",
                "cmd": "$ALIAS_PATH/gitrecon -r $WORKSPACE/gitscan/$OUTPUT-repo.txt -o '$WORKSPACE/gitscan/$OUTPUT' -k '$GITHUB_API_KEY' -p '$PLUGINS_PATH' ",
                "output_path": "$WORKSPACE/gitscan/$TARGET-gitrob.txt",
                "std_path": "$WORKSPACE/gitscan/std-$TARGET-gitrob.std"
            },
            {
                "requirement": "$WORKSPACE/gitscan/$OUTPUT-user.txt",
                "banner": "Git recon user",
                "cmd": "$ALIAS_PATH/gitrecon -u $WORKSPACE/gitscan/$OUTPUT-user.txt -o '$WORKSPACE/gitscan/$OUTPUT' -k '$GITHUB_API_KEY' -p '$PLUGINS_PATH' ",
                "output_path": "$WORKSPACE/gitscan/$TARGET-gitrob.txt",
                "std_path": "$WORKSPACE/gitscan/std-$TARGET-gitrob.std"
            }
        ],
    }
