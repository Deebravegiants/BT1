### Title
Webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` authenticates the body bytes only. The `shop-domain`, `topic`, `api-version` and `webhook-id` values are read straight from unauthenticated HTTP headers and handed to the app's handler as the tenant identity, without being part of the signed material.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) [2](#0-1) 

`to_signable_string` returns `@raw_body` exclusively — none of the `shopify-*` headers are included in the string that is HMAC-verified. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes `HMAC-SHA256(secret, to_signable_string)` and compares it (via `OpenSSL.secure_compare`) against `request.hmac`, i.e. it verifies the body only: [3](#0-2) [4](#0-3) 

After validation succeeds, `Registry.process` builds `WebhookMetadata` using `request.shop`, which is read directly from the `x-shopify-shop-domain` (or `shopify-shop-domain`) header: [5](#0-4) 

This is the same bug class as the `Float128::eq` finding: a value acted upon (the mantissa/exponent pair, or here the `shop` tenant identifier) is not the same value that was actually integrity-checked (the raw unwrapped bits, or here the signed body). The binding the gem should guarantee is:

`shop identity trusted by handler == shop identity covered by HMAC`

but the actual binding enforced is:

`bytes verified by HMAC (body only) ≠ bytes used to derive tenant identity (shop-domain header)`

Because Shopify's real webhook HMAC is computed only over the body (this matches Shopify's documented webhook verification scheme), this is consistent with upstream design rather than a coding defect introduced by this gem — the header was never meant to be authenticated by the HMAC. However, from the perspective of the "identity binding" bug class in the report (equating covered vs. uncovered bits), this is exactly such a mismatch: **an attacker who can replay/forward a legitimately-signed webhook body while forging/rewriting the `x-shopify-shop-domain` header** (e.g., a proxy, load balancer, or app hosting layer that does not itself pin the header, or an attacker submitting a raw HTTP request directly to the app's webhook endpoint bypassing Shopify) can cause the app to process the payload under an attacker-chosen `shop` value, because the gem itself performs no comparison between the header-derived shop and any signed value.

### Impact Explanation
If an app relies on `WebhookMetadata#shop` (as documented, this is the recommended way to identify the tenant for a webhook) to select which merchant's data to update/redact, an attacker who can reach the app's webhook endpoint with a validly-signed body (for any shop subscribed to that app) combined with a forged `shop-domain` header could cause the handler to attribute/act on data under a different shop id than the one that actually produced the payload — a cross-tenant data confusion. This requires the attacker to already possess a validly-signed webhook body (i.e., control of, or MITM access to, a real webhook delivery, or a hosting/proxy layer that allows header injection), which is a significant precondition.

### Likelihood Explanation
Low-to-moderate. This is not directly exploitable by an anonymous internet user against the gem alone — it requires either (a) a genuine HMAC-valid webhook body that the attacker can replay with a modified `shop-domain` header (e.g., via a vulnerable reverse proxy that lets client-supplied headers overwrite Shopify's), or (b) the app trusting `request.shop` as a security boundary while exposing the webhook endpoint to arbitrary header injection. The gem provides no built-in defense (i.e., it does not bind `shop` into the signed material or independently verify shop identity against session/shop records), so any host application that treats `request.shop`/`WebhookMetadata#shop` as authenticated is at risk purely due to header trust, matching the "field acted on but not covered by the HMAC" analog class.

### Recommendation
- Document prominently (and/or enforce in the gem) that `shop-domain` is **not** authenticated by the webhook HMAC and must not be treated as a trusted tenant identifier on its own; require callers to cross-check `WebhookMetadata#shop` against a known/registered shop (e.g., an existing session or webhook subscription record) before performing shop-scoped writes.
- Alternatively, extend the signable string (where compatible with Shopify's signing scheme) or add a secondary integrity check that binds the shop identity to the verified payload before constructing `WebhookMetadata`.
- At minimum, raise this in `Registry.process` — reject requests where the derived `shop` is not present in the app's known list of shops, if such a list is available to the host app via a supplied callback.

### Proof of Concept
Conceptual PoC (cannot be executed without the app's `client_secret`, which is required to produce a valid HMAC in the first place — this limits practical exploitation to header-injection/replay scenarios):

```ruby
raw_body = '{"id":123,"note":"legit shop A payload"}'
hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)
signed_hmac_header = Base64.strict_encode64([hmac].pack("H*"))

# Attacker (or a misconfigured proxy) rewrites shop-domain while keeping the same signed body
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => signed_hmac_header,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-api-version" => "2024-01",
  "x-shopify-webhook-id" => "1",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) still returns true, because it only checks raw_body,
#    and the handler receives WebhookMetadata with shop: "victim-shop.myshopify.com"
``` [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
