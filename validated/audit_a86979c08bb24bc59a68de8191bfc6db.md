### Title
Webhook Shop Identity Not Bound by HMAC Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop-tenant identity from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, but the gem's HMAC verification (`Utils::HmacValidator.validate`) only ever signs/verifies the raw request body. Any actor who can obtain one validly-signed webhook (e.g. by installing the target's public app on their own store) can replay that exact body with a forged `shop-domain` header naming a different (victim) shop, and the signature will still validate, because the shop identity is never part of the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `#shop` — the tenant identity later trusted by the app — is read straight from an unsigned header: [2](#0-1) 

`Registry.process` verifies the request purely via `Utils::HmacValidator.validate(request)` (i.e. HMAC over the body only) and then hands `request.shop` straight to the app's handler as the authoritative tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes the signature exclusively from `verifiable_query.to_signable_string`, which for webhooks is the raw body — the shop domain header is never included in the signable string: [4](#0-3) 

The binding the code implicitly assumes is:
`shop_identity_trusted_by_handler == shop_identity_covered_by_hmac`

but in reality:
`shop_identity_trusted_by_handler (header "shopify-shop-domain") ≠ bytes_covered_by_hmac (raw_body only)`

Because a single `client_secret`/app signs webhooks for *every* store that installs the app (this is a multi-tenant secret, not a per-shop secret), any unprivileged user can install the target's (public) app on their own store, receive a legitimately HMAC-signed webhook for their own shop, and then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still return `true` since it only checks the body signature, and `Registry.process` will invoke the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks tenant isolation: the app-level handler (which typically looks up/updates per-shop state, and for the mandatory GDPR topics `shop/redact`, `customers/redact`, `customers/data_request` performs destructive/privacy-sensitive operations) will act on attacker-controlled data while believing it belongs to the victim shop. An attacker can inject spoofed data attributed to a shop they don't own, or trigger privacy/redaction workflows against a shop they don't control — i.e., cross-tenant access, matching the "Critical – cross-tenant access" impact bucket.

### Likelihood Explanation
The attack requires only that the app is a public/installable app (the normal case) and that the attacker can install it on a store they control — no privileged credentials, `api_secret_key`, or access token are needed, and no host-application misuse is required since the vulnerable check lives entirely inside `HmacValidator`/`Webhooks::Request` in this gem.

### Recommendation
Include the shop domain (and ideally webhook id / topic) inside the HMAC-signed bytes, or otherwise cryptographically bind the `shopify-shop-domain` header to the verified payload before trusting it (e.g. verify the shop against a known/installed-shop list keyed by an already-authenticated session, rather than trusting the header value directly once the body-only HMAC passes).

### Proof of Concept
```ruby
# Attacker installs the target app on their own store "attacker.myshopify.com"
# and receives a legitimate webhook, e.g. for topic "customers/redact":
raw_body = '{"customer":{"id":123},"shop_id":999}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker now replays the SAME body/hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to a victim they don't own:
headers = {
  "shopify-topic" => "customers/redact",
  "shopify-hmac-sha256" => Base64.encode64(hmac),
  "shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by hmac
  "shopify-webhook-id" => "spoofed-id",
  "shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# Passes HMAC validation because only raw_body is signed/verified:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process will invoke the handler with shop == "victim-shop.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(request)
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
