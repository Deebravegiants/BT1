### Title
Webhook HMAC Only Signs Raw Body, Allowing Shop-Domain/Topic Spoofing and Cross-Tenant Webhook Injection - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then trusts the `shopify-shop-domain` and `shopify-topic` HTTP headers verbatim to decide which tenant/topic the payload belongs to. Because those headers are never included in the signed material, any party who can obtain one valid `(body, hmac)` pair for the shared app secret (e.g., by legitimately receiving a webhook for their own store) can replay that exact body with a forged `shopify-shop-domain`/`shopify-topic` header, and the signature will still validate. This breaks the identity binding between "bytes verified" and "shop credited," the same class of flaw described in the source report (a value that is acted upon but never validated against what was actually authenticated).

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes/compares the HMAC exclusively over `verifiable_query.to_signable_string`, i.e., the raw body — nothing else: [2](#0-1) 

`Registry.process` validates that HMAC and, once it passes, unconditionally trusts `request.shop` and `request.topic` — both parsed straight from headers — to select the handler and to build the `WebhookMetadata` passed to application code: [3](#0-2) 

`request.shop` and `request.topic` are read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` and `shopify-topic`/`x-shopify-topic` headers with no cryptographic tie to the signed body: [4](#0-3) 

Since all shops installing the same app share one `api_secret_key` for webhook signing, any merchant who has installed the app can legitimately receive a real webhook `(body, hmac)` pair addressed to their own shop. That pair remains valid regardless of which `shopify-shop-domain`/`shopify-topic` header values are attached to the replayed request, because those fields are outside the signed content. The equality the code implicitly (and incorrectly) assumes is:

`shop credited to the handler (header) == shop that produced the signed bytes (implicit, unchecked)`

but the code only ever proves `hmac == HMAC(body, secret)`; it never proves the header-declared shop/topic match the body's true origin.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an authenticated app user (any merchant with the app installed) can forge webhook deliveries that the app will process as though they originated from an arbitrary other shop or a different topic, while still passing `HmacValidator.validate`. Depending on what the app's webhook handlers do with `WebhookMetadata#shop` (e.g., look up/update per-shop records, trigger shop-scoped side effects, or gate GDPR/compliance topics like `customers/redact`), this enables cross-tenant data corruption, spoofed shop lifecycle events (e.g., forged `app/uninstalled` or `shop/redact` for a victim shop), or misattribution of webhook payloads between tenants — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that has more than one merchant installed: no special access beyond a normal app installation is required. The attacker simply needs to capture a webhook payload that Shopify legitimately signed and delivered to their own endpoint, then resend it with tampered `shopify-shop-domain`/`shopify-topic` headers. No knowledge of `api_secret_key` is required since the attacker already holds a validly-signed `(body, hmac)` pair.

### Recommendation
Do not derive tenant/topic identity solely from unauthenticated headers once only the body is verified. Options:
- Include `shop-domain`, `topic`, `webhook-id`, and `api-version` in the HMAC-signed material (or independently verify them, e.g., cross-checking `shop-domain` against the session/shop the app expects, and validating `webhook-id` uniqueness/idempotency).
- At minimum, document and enforce that handlers must independently authorize/validate the `shop` value (e.g., against a known list of installed shops) before trusting it for any state-changing or shop-scoped action.

### Proof of Concept
1. Merchant "attacker-shop.myshopify.com" installs the target app; Shopify sends a legitimate webhook to the app's endpoint:
   - Headers: `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: orders/create`, `shopify-hmac-sha256: <valid HMAC over BODY>`
   - Body: `BODY`
2. Attacker replays the exact same `BODY` and `shopify-hmac-sha256` value, but changes:
   - `shopify-shop-domain: victim-shop.myshopify.com`
   - (optionally) `shopify-topic` to another topic the app supports.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `BODY` — this still matches, since the body is unchanged.
4. The handler executes with `WebhookMetadata.new(topic: <attacker-chosen>, shop: "victim-shop.myshopify.com", body: <attacker's original body>, ...)`, causing the app to process attacker-controlled data as if it belongs to `victim-shop.myshopify.com`. [3](#0-2) [1](#0-0)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
