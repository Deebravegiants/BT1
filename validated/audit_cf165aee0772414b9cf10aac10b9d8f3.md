### Title
Webhook shop-domain (and topic) header not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shopify-shop-domain` and `shopify-topic` HTTP headers—values that are never included in the signed bytes—to build the `WebhookMetadata` passed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled straight from HTTP headers, which are outside the HMAC-signed payload: [2](#0-1) 

`HmacValidator.validate` only recomputes the signature over `to_signable_string` (the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authentication for the *entire* request, including the shop identity, and forwards the header-derived shop straight to the handler: [4](#0-3) 

`WebhookMetadata.shop` is defined as a plain, unauthenticated `String` field that handlers use to identify which merchant/tenant the event belongs to: [5](#0-4) 

**Broken binding (equality that should hold but doesn't):**
`hmac == HMAC(secret, bytes_that_include_shop)` is what the code implicitly assumes, but in reality it only checks `hmac == HMAC(secret, raw_body)`, while `shop` is read from an unsigned header. Concretely: `verified_bytes (raw_body) != acted_on_identity (shop header)`.

Because Shopify's own webhook signing scheme legitimately produces a valid `raw_body` + `hmac` pair for *any* shop that has installed the app (including a shop controlled by the attacker), an attacker who owns an install of the app can:
1. Trigger a real webhook delivery to their own endpoint/shop, capturing a genuine `(raw_body, hmac)` pair signed with the app's `client_secret`.
2. Replay that exact `raw_body` and `hmac` header to the app's public webhook endpoint, but substitute the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds because it only checks the untouched `raw_body` against the untouched `hmac`; the swapped header is never covered by the signature.
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: <victim-shop>, body: <attacker-controlled-parsed-body>, ...)`, so the application logic executes attacker-supplied webhook data under the identity of a shop the attacker never controls.

This is a direct instance of the requested analog class: "a field acted on but not covered by the HMAC" — the shop identity used downstream (to select a per-tenant session/access token, update per-tenant records, or drive business logic) is not bound to the signature that authenticates the payload.

### Impact Explanation
Any code path that keys off `WebhookMetadata#shop` to look up the corresponding merchant session/access token, or that performs actions in the "named" shop's context (e.g. writing data, invalidating caches, updating installation state, or forwarding the payload to the merchant's own database keyed by shop), can be tricked into acting for a shop the requester does not control, using attacker-crafted body content. This is a cross-tenant access primitive: an install belonging to Shop A can inject events attributed to Shop B. This matches the "Critical: cross-tenant access" impact bucket.

### Likelihood Explanation
The attack requires only that the attacker install (or already have installed) the app on any shop they control — no special privilege, leaked secret, or access token is required, and no TLS interception or social engineering is needed. Public webhook endpoints are internet-reachable by design, and header spoofing (setting arbitrary `shopify-shop-domain` header values) is trivial for an unprivileged internet user making raw HTTP requests. The gem provides no header-canonicalization/binding, so any consuming application is exposed unless it independently re-validates the shop header against something signed (which the library gives it no way to do).

### Recommendation
Bind the shop identity (and ideally topic/webhook-id) to the signed material, or at minimum instruct/require consuming apps to cross-check the header-derived `shop` against an installation record obtained via a channel that is itself authenticated (e.g., verifying the shop against a previously stored session for that shop before trusting webhook content), rather than allowing `Registry.process` to hand back a `WebhookMetadata` whose `shop` field was never covered by the signature. At minimum, document prominently that `shop`/`topic` headers are unauthenticated and must not be trusted for tenant-sensitive decisions without additional verification by the host application.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the app.
# Shopify legitimately delivers a webhook to the attacker for their own shop:
raw_body = '{"id": 1, "malicious": "payload"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), Context.api_secret_key, raw_body)
)

# Attacker replays the exact body+hmac to the victim's webhook endpoint,
# spoofing the shop-domain header:
forged_headers = {
  "shopify-topic" => "orders/create",
  "shopify-hmac-sha256" => valid_hmac,       # still valid: HMAC only covers raw_body
  "shopify-shop-domain" => "victim-shop.myshopify.com",  # NOT covered by HMAC
  "shopify-webhook-id" => "attacker-controlled-id",
  "shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/hmac match),
#    handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body, ...))
#    is invoked as if Shopify sent this event for victim-shop, though the
#    payload/body was fully controlled by the attacker.
``` [1](#0-0) [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
