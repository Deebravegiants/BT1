# [M] CVE-2020-36635

## Summary
Severity: Medium
Advisory: CVE-2020-36635
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-12-27
Source: https://osv.dev/vulnerability/CVE-2020-36635
Type: osv

## Details
A vulnerability was found in OpenMRS Appointment Scheduling Module up to 1.12.x. It has been classified as problematic. This affects the function validateFieldName of the file api/src/main/java/org/openmrs/module/appointmentscheduling/validator/AppointmentTypeValidator.java. The manipulation leads to cross site scripting. It is possible to initiate the attack remotely. Upgrading to version 1.13.0 is able to address this issue. The name of the patch is 34213c3f6ea22df427573076fb62744694f601d8. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216915.

## References
- https://github.com/openmrs/openmrs-module-appointmentscheduling/releases/tag/1.13.0
- https://vuldb.com/?ctiid.216915
- https://vuldb.com/?id.216915
- https://github.com/openmrs/openmrs-module-appointmentscheduling/commit/34213c3f6ea22df427573076fb62744694f601d8
- https://github.com/openmrs/openmrs-module-appointmentscheduling/pull/32
