# [M] Negotiate ambient user conn reuse

## Summary
Severity: Medium
Advisory: CURL-CVE-2026-19931
Aliases: CVE-2026-19931
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CURL-CVE-2026-19931
Type: osv

## Details
A flaw in libcurl makes it wrongly reuse an HTTP connection setup for a given
hostname using Negotiate authentication, when the initial request is done
using empty credentials. This can make user B's request get sent over user A's
previously authenticated connection.
