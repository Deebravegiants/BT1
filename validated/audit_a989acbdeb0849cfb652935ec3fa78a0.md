### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies is computed only over `to_signable_string`, which returns the raw request body. The identity binding `hmac_validated_bytes == tenant_identifier_used_downstream` does not hold: the byte range Shopify signs (the body) and the field the gem hands to the host application for tenant/session routing (`request.shop`, sourced from a header) are disjoint.

### Finding Description
`Request#shop` is derived purely from a header value that carries no cryptographic binding to the payload: [1](#0-0) 

The HMAC that the gem verifies (`hmac`) is parsed from the `hmac-sha256` header, and the value that is actually authenticated (`to_signable_string`) is only the raw body: [2](#0-1) [3](#0-2) 

The constructor validates only that the required headers are *present*, not that any of them (topic, shop-domain, api-version, webhook-id) are covered by the signature: [4](#0-3) 

Because `HmacValidator.validate` (referenced in `lib/shopify_api/utils/hmac_validator.rb`, used generically via `Utils::VerifiableQuery`) only recomputes and compares the HMAC over `to_signable_string` (the body), a successful validation proves the *body* came from someone possessing the app's `client_secret`-derived signing key context, but proves nothing about the `shop-domain` header that accompanies it. This mirrors the reported bug class exactly: a field that the application acts on (here, the shop used to route/authorize the webhook) is not covered by the same integrity check (HMAC) that is otherwise relied upon to authenticate the request — analogous to `completeInboundQueuedTransfer` acting on chain state without the `checkFork` binding that `executeMsg` enforces.

### Impact Explanation
Any host application that follows this gem's documented pattern — verifying a webhook via `HmacValidator.validate(request)` and then dispatching/authorizing using `request.shop` — can be made to process a webhook body under the wrong tenant identity. An attacker who can obtain one legitimately-signed webhook body for the shared app (e.g., by installing the app on their own store and capturing a delivered webhook, or by controlling any shop that installs the app) can resend that exact byte-identical body with the same valid HMAC but a substituted `shopify-shop-domain` header pointing at a victim shop. Validation still succeeds because the HMAC never covered the header, causing the host application to attribute attacker-controlled webhook data to a victim tenant — a cross-tenant integrity violation.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one genuinely-signed webhook payload for the app (obtainable by installing the app on an attacker-owned/trial shop, which is not privileged access to any victim) and requires the webhook endpoint to be reachable, which it is by design (webhook receivers are public HTTP endpoints). No access token, `client_secret`, or privileged credential is needed. Likelihood is moderate: it depends on host applications trusting `request.shop` post-validation without an additional out-of-band tenant check, which is the pattern this gem's API implicitly encourages by exposing `shop` as a first-class accessor on the validated `Request` object.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) value into the signed material checked by `HmacValidator`, or explicitly document/enforce that `request.shop` must never be used for authorization decisions without corroborating it against a known/allow-listed shop for the given webhook subscription. Concretely, extend `to_signable_string` (or add a secondary check in `Request`) so shop-domain is cryptographically bound to the same HMAC verification path used for the body, closing the gap between "authenticated bytes" and "bytes acted upon" — consistent with the reported pattern of the missing `checkFork` binding in `completeInboundQueuedTransfer`.

### Proof of Concept
1. Attacker installs the app on an attacker-controlled shop `attacker.myshopify.com`, triggering a legitimate webhook delivery with a valid `X-Shopify-Hmac-SHA256` header computed over the raw body by Shopify using the app's secret.
2. Attacker captures this raw body + HMAC header pair.
3. Attacker crafts a POST to the app's webhook endpoint reusing the identical raw body and HMAC header, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into `shop == "victim.myshopify.com"` while `to_signable_string` (the body) remains unchanged; `Utils::HmacValidator.validate(request)` recomputes HMAC over the body and it matches, so validation passes.
5. A host application that trusts `request.shop` post-validation (per the gem's documented `Request#shop` API) processes attacker-controlled data as if it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
      end
```
