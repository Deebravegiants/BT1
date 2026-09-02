### Title
Webhook `shop` (and `topic`/`webhook_id`) fields are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` — the value that `HmacValidator` verifies — returns only the raw request body. The `shop`, `topic`, and `webhook_id` values consumed by `ShopifyAPI::Webhooks::Registry.process` are read from unauthenticated HTTP headers that are not included in the HMAC computation at all. Any party capable of obtaining one validly-signed webhook body (e.g. a merchant who has the app installed on their own store and receives genuine webhooks from Shopify) can replay that body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a different (victim) shop. `HmacValidator.validate` will accept the request, because it only re-computes and compares the HMAC over the body, and `Registry.process` will hand the host application a `WebhookMetadata` object whose `shop` attribute is the attacker-chosen value.

### Finding Description
The identity binding that should hold is:
`hmac == HMAC(secret, bytes_verified)` should imply `bytes_verified` includes every field the host application subsequently trusts as authenticated, in particular `shop`.

In this gem that equality does not hold: [1](#0-0) 

- `hmac` is read from the `hmac-sha256` header.
- `shop`, `topic`, `api_version`, `webhook_id` are all read from other headers.
- `to_signable_string` — the only bytes actually verified — returns `@raw_body` alone.

`HmacValidator.validate` only ever calls `to_signable_string` to build the value it HMACs: [2](#0-1) 

`Registry.process` gates on this HMAC check and then immediately forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` fields to the handler as if they were verified: [3](#0-2) 

So the flow is:
1. Attacker's own store (which they legitimately control) generates a real webhook event; Shopify sends it to the app's endpoint, HMAC-signed over the body with the app's `api_secret_key`.
2. Attacker captures that request (they control the receiving traffic to their own account/proxy, or simply reuse a body they already know, e.g. an order-creation body whose shape is predictable) and re-sends it to the same endpoint, keeping the body and its valid `hmac` header untouched but changing `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `HmacValidator.validate` recomputes the HMAC over `@raw_body` only — identical to the original — and returns `true`.
4. `Registry.process` builds `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` and calls the host app's handler, which typically uses `shop` to look up/create the tenant record to write into (per the library's own webhook usage guidance and typical `shopify_app` style handler implementations).

This is a "field acted on but not covered by the HMAC" identity-binding break: the host application's authorization decision (which tenant's data to mutate) is keyed on `shop`, but `shop` is not part of what the HMAC actually authenticates.

### Impact Explanation
This crosses the tenant boundary described in scope ("cross-tenant access"): an unprivileged party who only has access to their own installed app instance can forge webhook events that the host application will process under a different merchant's identity, without ever needing the app's `client_secret`, `api_secret_key`, or any access token. Depending on the handler logic in the host app (which the gem's docs encourage keying off `WebhookMetadata#shop`), this can lead to data being written to, or read/inferred about, another merchant's account.

### Likelihood Explanation
Requires only: (a) an app installed by the attacker on their own shop so a genuinely HMAC-valid body/signature pair can be obtained (attacker fully controls when/what events they can trigger, e.g. `orders/create`), and (b) the ability to replay an HTTP request to the app's public webhook endpoint with a modified header — both of which are within the reach of any "unprivileged internet user" who is a customer of the app being built on this gem. No secrets, tokens, or elevated access are required.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value that gets HMAC-verified, or otherwise cryptographically tie the header-derived shop domain to the signed payload before trusting it. At minimum, `Webhooks::Request#to_signable_string` should not be the sole gate — the library should expose/require verification that the `shop` header matches an expected/registered shop for the delivery, or document unambiguously (and enforce via API) that `shop` must be independently corroborated against a known/registered store before being used for tenant selection. Concretely, the gem should either include the shop-domain and topic headers in the signable string it feeds to `HmacValidator`, or provide a dedicated authenticated accessor that fails closed unless the caller supplies the shop it expects to receive.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own store and captures a legitimately
#    signed webhook delivery, e.g. an "orders/create" POST with:
raw_body = '{"id":1,"email":"attacker@example.com"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac), # untouched, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- attacker-controlled, not covered by hmac
  "x-shopify-webhook-id" => "attacker-chosen-id",
}

# 2. Replay to the app's public webhook endpoint.
request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. HmacValidator.validate(request) returns true because it only checks raw_body.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "orders/create", body: {...}))
```
The host application's handler receives `shop: "victim-shop.myshopify.com"` as if it were an authenticated fact, despite the attacker having no relationship with, or credentials for, that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
