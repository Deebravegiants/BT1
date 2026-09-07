# [M] opentelemetry-collector-contrib sentryexporter: Path traversal in Sentry exporter via attacker-controlled service.name reaches privileged Sentry API endpoints with operator bearer token

## Summary
Severity: Medium
Advisory: GHSA-4jvg-4jfx-fmhc
CVE: CVE-2026-47256
CWE: CWE-22, CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-4jvg-4jfx-fmhc
Type: github-advisory

## Affected
- Go: `github.com/open-telemetry/opentelemetry-collector-contrib/exporter/sentryexporter` — affected >=0 <0.154.0

## Details
Summary               
         
  The Sentry exporter constructs Sentry API URLs by interpolating the span's service.name resource attribute into the URL path without validation. Because
  service.name is controlled by remote OTLP senders and the operator-configured bearer token is attached to every request, a crafted service name can reach
  arbitrary Sentry API endpoints reachable by that token — including privileged admin, organization, and member endpoints within the configured Sentry
  organization.                                                                                                                                               
                                          
  Affected                                                                                                                                                    
                                                                                                                                                              
  - exporter/sentryexporter/sentry_exporter.go (lines 715–737) — extractProjectSlug returns the attacker-controlled service.name directly as the slug.        
  - exporter/sentryexporter/sentry_exporter.go (lines 745–809) — getOrCreateProjectEndpoint passes the raw slug to GetOTLPEndpoints at line 761.              
  - exporter/sentryexporter/sentry_client.go (lines 190–244) — GetProjectKeys interpolates the slug into fmt.Sprintf URL path and attaches the operator bearer
   token on line 207.                                                                                                                                         
  - exporter/sentryexporter/sentry_client.go (lines 327–363) — GetOTLPEndpoints calls GetProjectKeys on line 329 with the raw slug.
  - exporter/sentryexporter/config.go (lines 55–108) — projectSlugRegexp is applied only to operator config mappings inside validateRoutingConfig, never to   
  runtime-derived slugs.                                                                                                                                      
                                                                                                                                                              
  Root cause                                                                                                                                                  
                                                                                                                                                              
  1. extractProjectSlug (sentry_exporter.go:715–737) reads service.name from pcommon.Resource.Attributes() without schema validation and returns the raw      
  string on line 736.                                                                                                                                         
  2. GetProjectKeys (sentry_client.go:192) calls fmt.Sprintf("%s/api/0/projects/%s/%s/keys/", c.baseURL, orgSlug, projectSlug). The slug is treated as a
  single path segment but no validation is performed.                                                                                                         
  3. projectSlugRegexp (config.go:58) — defined as ^[a-z0-9_-]{1,50}$ — is referenced only inside validateRoutingConfig on line 98 (config-time only). No
  runtime callsite exists.                                                                                                                                    
  4. Go net/http preserves literal .. and / characters in URL paths when constructed via fmt.Sprintf.                                                         
  5. The operator-configured DSN / bearer token is attached unconditionally to every outbound request (sentry_client.go:207): req.Header.Set("Authorization", 
  fmt.Sprintf("Bearer %s", c.authToken)).                                                                                                                     
                                            
  Exploitation                                                                                                                                                
                                                                                                                                                              
  Primary: query-string injection (reliable across all deployments)                                                                                           
                                                                                                                                                              
  Attacker emits service.name = "foo?injected_query=".
                                                                                                                                                              
  URL becomes https://sentry.io/api/0/projects/ORG-SLUG/foo?injected_query=/keys/.
                                                                                                                                                              
  The trailing /keys/ is consumed as part of the query string. The resource endpoint is /api/0/projects/ORG-SLUG/foo. The attacker can reach any GET-based
  Sentry API endpoint reachable by the bearer token. This vector is not dependent on server-side path normalization and works in all deployment               
  configurations.                           
                                                                                                                                                              
  Secondary: path traversal (nginx-dependent)
                                                                                                                                                              
  Attacker emits a span with service.name = "foo/../../members".
                                          
  Resulting URL: https://sentry.io/api/0/projects/ORG-SLUG/foo/../../members/keys/
                                                                                                                                                              
  After server-side normalization (nginx resolves .. segments): https://sentry.io/api/0/projects/ORG-SLUG/members/keys/
                                                                                                                                                              
  The operator bearer token authenticates the request. Effectiveness depends on whether the Sentry deployment normalizes .. segments before routing (standard
  nginx behaviour).                                                                                                                                           
                                            
  Amplified: telemetry redirect for data exfiltration                                                                                                         
                                            
  Attacker-owned Sentry project slug → span data for other applications is exported to an attacker-controlled Sentry project, leaking operational telemetry.  
  The collector fetches the DSN/keys for the attacker's slug and subsequently forwards legitimate traces/logs to the attacker-controlled destination.         
   
  Threat model                                                                                                                                                
                                            
  - Attacker capabilities: remote OTLP trace sender (application-level span emission).                                                                        
  - Operator capabilities: configures Sentry DSN, bearer token, base URL; sets up receiver pipeline.
  - The attacker does NOT control operator YAML. The attacker DOES control resource attribute values on spans they emit.
                                          
  Realistic deployment
                                                                                                                                                              
  - Kubernetes cluster with OpenTelemetry Collector forwarding traces from multiple applications to Sentry SaaS or self-hosted Sentry.
  - One compromised or malicious application reaches the collector via OTLP.                                                                                  
  - The collector is configured with a valid Sentry bearer token for the organization.

                                                                                                                                                              
  Remediation
                                                                                                                                                              
  Apply the existing projectSlugRegexp to runtime-derived slugs, not only to operator config mappings:
  ```                                                                                                                                                            
  import "regexp"                           

  var runtimeSlugPattern = regexp.MustCompile(`^[a-zA-Z0-9_-]+$`)
                                          
  func (s *endpointState) extractProjectSlug(attrs pcommon.Map) string {
      attrValue, exists := attrs.Get(s.attributeKey)                                                                                                          
      if !exists || attrValue.Type() != pcommon.ValueTypeStr {
          return ""                                                                                                                                           
      }                                     
      serviceName := attrValue.Str()                                                                                                                          
      if serviceName == "" {
          return ""                                                                                                                                           
      }                                     
      if s.projectMapping != nil {
          if mappedSlug, ok := s.projectMapping[serviceName]; ok {                                                                                            
              return mappedSlug
          }                                                                                                                                                   
      }                                     
      if !runtimeSlugPattern.MatchString(serviceName) {
          return "" // reject; drop the span or use a fallback default project
      }
      return serviceName                                                                                                                                      
  }
                                                                                                                                                              
  Alternatively, reject at URL construction:  
                                          
  func (c *sentryClient) GetProjectKeys(ctx context.Context, orgSlug, projectSlug string) ([]projectKey, error) {
      if !runtimeSlugPattern.MatchString(projectSlug) {                                                                                                       
          return nil, fmt.Errorf("invalid project slug: %q", projectSlug)
      }                                                                                                                                                       
      baseURL := fmt.Sprintf("%s/api/0/projects/%s/%s/keys/", c.baseURL, orgSlug, projectSlug)
      // ...                                                                                                                                                  
  }                                       
```                                                                                                                                                              
  Apply the runtime regex to ALL slug-derived URL components (including orgSlug if it can ever be attacker-influenced), not just to config-time validation.   
   
  Credit                                                                                                                                                      
                                            
  Reported by independent security research by Martin Brodeur.

## References
- https://github.com/open-telemetry/opentelemetry-collector-contrib/security/advisories/GHSA-4jvg-4jfx-fmhc
- https://github.com/open-telemetry/opentelemetry-collector-contrib
