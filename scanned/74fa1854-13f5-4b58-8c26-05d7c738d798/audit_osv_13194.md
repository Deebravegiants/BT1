# [M] CVE-2018-18558

## Summary
Severity: Medium
Advisory: CVE-2018-18558
CVSS: 6.4 (CVSS:3.0/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-13
Source: https://osv.dev/vulnerability/CVE-2018-18558
Type: osv

## Details
An issue was discovered in Espressif ESP-IDF 2.x and 3.x before 3.0.6 and 3.1.x before 3.1.1. Insufficient validation of input data in the 2nd stage bootloader allows a physically proximate attacker to bypass secure boot checks and execute arbitrary code, by crafting an application binary that overwrites a bootloader code segment in process_segment in components/bootloader_support/src/esp_image_format.c. The attack is effective when the flash encryption feature is not enabled, or if the attacker finds a different vulnerability that allows them to write this binary to flash memory.

## References
- https://www.espressif.com/en/news/Espressif_Product_Security_Advisory_Concerning_Secure_Boot_%28CVE-2018-18558%29
- https://github.com/espressif/esp-idf/releases
