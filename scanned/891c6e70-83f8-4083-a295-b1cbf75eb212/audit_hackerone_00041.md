# [M] CVE-2024-8096: OCSP stapling bypass with GnuTLS

## Summary
Severity: Medium
Program: curl
Weakness: Improper Certificate Validation
Reporter: kurohiro
State: resolved
Disclosed: 2024-09-11T14:50:38.654Z
CVE: CVE-2024-8096
Source: https://hackerone.com/reports/2669852

## Details
## Summary:
When the TLS backend is GnuTLS, there is an issue with the OCSP stapling validation process. As a result, even if the certificate is revoked, the connection can be established without resulting in an error.

When the OCSP stapling status response is "revoked," gnutls_certificate_verify_peers2() returns an error. However, gnutls_certificate_verify_peers2() only returns an error when the OCSP status is "revoked." For other statuses, gnutls_certificate_verify_peers2() returns a successful result.

In curl, the verification of the OCSP stapling status response is performed not only with the above function but also with gnutls_ocsp_status_request_is_checked(). However, this function returns a non-zero value if the OCSP stapling status response exists. As a result, if any response exists, it is treated as a successful case, and the verification process concludes.

```
  if(config->verifystatus) {
    if(gnutls_ocsp_status_request_is_checked(session, 0) == 0) {
      gnutls_datum_t status_request;
      gnutls_ocsp_resp_t ocsp_resp;

      gnutls_ocsp_cert_status_t status;
      gnutls_x509_crl_reason_t reason;

      rc = gnutls_ocsp_status_request_get(session, &status_request);

      infof(data, " server certificate status verification FAILED");

      if(rc == GNUTLS_E_REQUESTED_DATA_NOT_AVAILABLE) {
        failf(data, "No OCSP response received");
        return CURLE_SSL_INVALIDCERTSTATUS;
      }

      if(rc < 0) {
        failf(data, "Invalid OCSP response received");
        return CURLE_SSL_INVALIDCERTSTATUS;
      }

      gnutls_ocsp_resp_init(&ocsp_resp);

      rc = gnutls_ocsp_resp_import(ocsp_resp, &status_request);
      if(rc < 0) {
        failf(data, "Invalid OCSP response received");
        return CURLE_SSL_INVALIDCERTSTATUS;
      }

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2669852_
