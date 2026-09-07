# [C] General OpenMRS Security Advisory, January 2025: Penetration Testing Results and Patches

## Summary
Severity: Critical
Advisory: GHSA-vpxm-cr3r-pjp9
CWE: CWE-209, CWE-284, CWE-601, CWE-614
Ecosystem: Maven
Published: 2025-01-30
Source: https://github.com/advisories/GHSA-vpxm-cr3r-pjp9
Type: github-advisory

## Affected
- Maven: `org.openmrs:openmrs` — affected >=0 <2.6.11
- Maven: `org.openmrs.module:legacyui` — affected >=0 <1.21.0
- Maven: `org.openmrs.module:idgen` — affected >=0 <4.14.0
- Maven: `org.openmrs.module:addresshierarchy` — affected >=0 <2.19.0
- Maven: `org.openmrs.module:attachments` — affected >=0 <3.6.0
- Maven: `org.openmrs.module:patientflags` — affected >=0 <3.0.8

## Details
### Impact
We recently underwent Penetration Testing of OpenMRS by a third-party company. **Vulnerabilities were found, and fixes have been made and released.** We've released security updates that include critical fixes, and so, we strongly recommend upgrading affected modules.

**This notice applies to _all_ OpenMRS instances.** The testers used the OpenMRS v3 Reference Application (O3 RefApp); however, their findings highlighted modules commonly used in older OpenMRS applications, including the O2 RefApp. 

## Vulnerability Details
- The issues uncovered included broken access control (e.g. inappropriate admin access), phishing vulnerability, and stored XSS (e.g. vulnerable passwords).
- No vulnerabilities were found in the O3 frontend esm modules. 
- The Letter of Attestation from the penetration test is [available here](https://drive.google.com/file/d/1sBm4-FzLA8hSoM9wYknBfgEttBHyLvoU/view?usp=sharing) for your reference. 
- After the fixes were applied, the OpenMRS O3 RefApp met a Security Level of “Excellent, Grade A”.
- The full detailed Remediation Pentest Report is available to Implementation Technical Leads upon request.

### Patches
**Minimum Requirements for Implementers:** We **strongly** recommend upgrading your modules to the following versions (or greater) as soon as possible. **This is the minimum amount to do and be protected from the vulnerabilities found and fixed.** The following versions contain the patch: 

- **Platform** 2.6.11+ 
  - How: Increase your platform version number wherever this is specified in your implementation. If you use the OpenMRS SDK, this will be in the distro.properties file.
  - Notes: 
    - The newly released [**Platform 2.7**](https://sourceforge.net/projects/openmrs/files/releases/OpenMRS_Platform_2.7.0/) also includes the fixes. [Release Notes and more download options here](https://openmrs.atlassian.net/wiki/x/XoBzEQ).
    - Platform 2.6.8+ has most of the fixes, but these are broken if you don't use SSL, so Platform 2.6.11 or higher is preferred.
    - For those still on Platform 2.5+ such as the Bahmni ecosystem, the new [2.5.14](https://ci.openmrs.org/browse/TRUNK-CORE2-232) release includes the patch. _Bahmni note: The upcoming patch release for both Bahmni Lite and Bahmni Standard will incorporate these security fixes._
- **Legacy UI** OMOD 1.21.0+ ([here](https://addons.openmrs.org/show/org.openmrs.module.legacyui))
- **ID Gen** OMOD 4.14.0+ ([here](https://addons.openmrs.org/show/org.openmrs.module.idgen))
- **Address Hierarchy** OMOD 2.19.0+ ([here](https://addons.openmrs.org/show/org.openmrs.module.addresshierarchy))
- **Attachments** OMOD 3.6.0+ ([here](https://addons.openmrs.org/show/org.openmrs.module.attachments))
- **Patient Flags** OMOD 3.0.8+ ([here](https://addons.openmrs.org/show/org.openmrs.module.patientflags))

### Workarounds
There are no practical workarounds to fix or remediate the vulnerabilities without upgrading. Technically, you could remove the affected OMODs, but this would badly degrade the system's functionality.

## Thank you to our amazing Security contributors!
Thank you to security firm UnderDefense, and to the OpenMRS Security Group contributors for their patch support - specific thanks to Daniel Kayiwa, Samuel Lubwama, Ian Bacher, Rafal Korytkowski, and Michael Seaton.

## References
- https://github.com/openmrs/openmrs-core/security/advisories/GHSA-vpxm-cr3r-pjp9
- https://github.com/openmrs/openmrs-core
