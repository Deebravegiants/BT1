# [M] ppp pppdump pppdump.c dumpppp array index

## Summary
Severity: Medium
Advisory: CVE-2022-4603
CVSS: 4.3 (CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2022-4603
Type: osv

## Details
A vulnerability classified as problematic has been found in ppp. Affected is the function dumpppp of the file pppdump/pppdump.c of the component pppdump. The manipulation of the argument spkt.buf/rpkt.buf leads to improper validation of array index. The real existence of this vulnerability is still doubted at the moment. The name of the patch is a75fb7b198eed50d769c80c36629f38346882cbf. It is recommended to apply a patch to fix this issue. VDB-216198 is the identifier assigned to this vulnerability. NOTE: pppdump is not used in normal process of setting up a PPP connection, is not installed setuid-root, and is not invoked automatically in any scenario.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J43NP7ABHOCIWOFHWCH6ZCZOYKZH6723/
- https://vuldb.com/?id.216198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4603.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J43NP7ABHOCIWOFHWCH6ZCZOYKZH6723/
- https://nvd.nist.gov/vuln/detail/CVE-2022-4603
- https://github.com/ppp-project/ppp/commit/a75fb7b198eed50d769c80c36629f38346882cbf
