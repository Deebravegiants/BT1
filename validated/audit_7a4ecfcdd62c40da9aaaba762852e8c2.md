### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC over the raw request body only, then hands the handler a `shop` value that comes from a header that is never included in the signed bytes. Any tenant that has installed the app (and therefore possesses a valid, Shopify-issued body+HMAC pair for their own webhook deliveries) can replay that body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain`/`shopify-shop-domain` header for a different (victim) shop, and the gem will report the forged shop as authenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

and `shop` is read straight from a header with no cryptographic binding to the signature at all: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e. the body) and compares it to the `hmac` header value using `Context.api_secret_key`: [3](#0-2) 

`Registry.process` uses only this body-HMAC check as its authentication gate, then immediately forwards `request.shop` (the unauthenticated header) to the handler as the tenant identity: [4](#0-3) 

The identity binding that should hold is: `bytes verified by HMAC == bytes used to attribute the event to a tenant`. Here that equality is broken: the HMAC only proves the request body was produced with the app's shared `api_secret_key` (a secret shared across *every* shop that installs the app, not per-tenant), while the `shop` value used to route/attribute the webhook is taken from a header outside that signed data. Because the secret is shared across all installations of the same app, any shop that has legitimately received one webhook delivery (with a valid body+HMAC pair) can resend that exact body/HMAC to the app's public webhook endpoint with the `shop-domain` header rewritten to name a different, victim shop. `HmacValidator.validate` still succeeds (the body/HMAC pair is genuinely valid), and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant identity-binding break at the gem's authentication boundary: the primitive the gem exposes to host applications (`ShopifyAPI::Webhooks::Registry.process` / `WebhookMetadata#shop`) is documented and used as the authenticated tenant identifier for the webhook, but it is derived from bytes the HMAC never covers. Any application built on this gem that uses `WebhookMetadata#shop` (as returned by the library, exactly as designed) to select which merchant's data to update, without independently re-verifying tenant identity, can be made to apply another shop's data/action against a different shop's records — a cross-tenant confusion enabled directly by this gem's own validation logic, not by host-application misuse of an undocumented feature.

### Likelihood Explanation
Likelihood is constrained: the attacker must be a legitimate installer of the same app (to obtain at least one genuine body+HMAC pair from Shopify), and must know/guess a target shop domain to substitute into the header, and the impact depends on the host app trusting `shop` from webhook processing for tenant-scoped actions. This mirrors the "low likelihood, high impact" profile of the analog bug class (requires a specific, but attacker-achievable, action sequence) rather than being trivially exploitable by a fully anonymous party.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` value to the signed body before it is exposed via `WebhookMetadata`. At minimum, `Utils::HmacValidator`/`Webhooks::Request` should not allow verification to succeed for a body whose accompanying `shop` header was not part of what Shopify actually signed for that specific delivery; consider validating that headers match the same values used when Shopify computed the HMAC, or require the host app to cross-check `shop` against its own known merchant registry as a documented, enforced part of `Registry.process`.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (same app, same `api_secret_key`).
2. Shopify sends a real webhook to the attacker's shop; the attacker captures the raw body `B` and the corresponding `x-shopify-hmac-sha256` header `H` (a valid HMAC-SHA256 of `B` with the shared `api_secret_key`), as computed in [5](#0-4) .
3. Attacker POSTs to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body per [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `B`/`H` are a genuinely valid pair.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim-shop.myshopify.com"`, as shown in [7](#0-6) , causing the app to process the attacker's payload under the victim's identity.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
