### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body via `Utils::HmacValidator.validate(request)` [1](#0-0) . The `shop` identity that is subsequently handed to the app's handler as the authoritative tenant for the webhook is read from an HTTP header (`shopify-shop-domain`/`x-shopify-shop-domain`) that is **not** included in the signable string used to compute/verify the HMAC [2](#0-1) [3](#0-2) . This breaks the identity binding `shop authenticated == shop acted on`: the bytes verified by HMAC (body only) are not the bytes that determine which tenant the webhook is processed for (the header).

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `Webhooks::Request#shop` is derived independently from a header that is never mixed into that signable string:
```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [4](#0-3) 

`Registry.process` validates only this body-based HMAC, then immediately trusts `request.shop` as the tenant identity passed to the app's handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [5](#0-4) 

`HmacValidator.validate_signature` performs a constant-time compare of the computed HMAC against the received one, but the computed HMAC is only over `to_signable_string` (the body), never over `shop`:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [6](#0-5) 

This is in stark contrast to the OAuth callback path, where `AuthQuery#to_signable_string` explicitly includes `shop` in the signed parameter set, correctly binding shop identity to the HMAC [7](#0-6) . The webhook path has no equivalent binding.

**Attack scenario:** An attacker who operates their own Shopify shop (unprivileged with respect to any other tenant) installs the victim app and triggers a webhook topic whose body is invariant or attacker-influenced (e.g., an empty/near-static payload). Shopify computes and sends a genuine `X-Shopify-Hmac-Sha256` for that body using the app's own `client_secret` — a secret the attacker never needs to know, because Shopify computed it. The attacker captures this valid `(body, hmac)` pair from their own delivery, then replays the same body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. Because `shop` is excluded from the signable string, `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` forwards `shop: <victim-domain>` to the app's handler as if the event genuinely originated from the victim tenant.

### Impact Explanation
This is a cross-tenant identity confusion: the gem allows a value that determines which merchant/tenant a webhook event is attributed to be forged independently of the cryptographic authentication, using only a body+HMAC pair the attacker can legitimately obtain for their own tenant. Any app relying on `WebhookMetadata#shop` (as documented and exercised throughout `Registry`/`Request`) to select the tenant record, session, or downstream action processes attacker-chosen data under an arbitrary victim shop's identity — a cross-tenant access impact.

### Likelihood Explanation
Any internet user can install a free/dev Shopify store to become a legitimate webhook sender for their own tenant, requiring no privileged credentials, access token, or knowledge of the app's `client_secret`. The only prerequisite is a webhook topic/body that is static or attacker-controllable enough to be replayed against another shop, which is realistic for several topics (e.g., topics with minimal or predictable JSON bodies).

### Recommendation
Bind the tenant identity into the authenticated bytes: include `shop`/`shop-domain` (and ideally `topic`, `webhook-id`) in the value verified against `X-Shopify-Hmac-Sha256`, or independently verify that the header-derived `shop` matches a shop value embedded in the verified body/claims, mirroring the approach already used in `AuthQuery#to_signable_string`.

### Proof of Concept
1. Attacker installs the app on their own dev shop `attacker.myshopify.com` and configures/triggers a webhook whose body content is static or attacker-controlled (e.g., `"{}"`).
2. Shopify sends the webhook to the app with a valid `X-Shopify-Hmac-Sha256` computed over that body using the app's `client_secret`.
3. Attacker captures the `(raw_body, hmac_header)` pair (they own the endpoint or a proxy in front of it).
4. Attacker resends the exact same body and HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `body` vs `hmac` [1](#0-0) .
6. The handler receives `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)` [8](#0-7) , causing the app to act on the victim tenant using attacker-supplied data.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
