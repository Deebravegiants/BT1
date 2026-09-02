## Finding [1](#0-0) 

The webhook `Request` class exposes `shop` from the `x-shopify-shop-domain` (or `shopify-shop-domain`) HTTP header, but `to_signable_string` — the value that the HMAC is computed over — returns only the raw request body:

```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end

def to_signable_string
  @raw_body
end
```

`Registry.process` validates the request purely on this body-only HMAC and then trusts `request.shop` as the tenant identifier passed to the app's handler: [2](#0-1) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

### Title
Webhook `shop` (and `topic`) header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body [3](#0-2)  whereas `Registry.process` uses the unauthenticated `shop` header to identify which tenant's data/session the webhook belongs to [4](#0-3) . This breaks the equality that should hold: `shop attributed to the payload == shop that produced/authorized the payload`. Contrast this with the OAuth callback path, where `AuthQuery#to_signable_string` explicitly includes `shop` in the signed string [5](#0-4) , so the same binding class of bug does not exist there.

### Finding Description
Any entity that legitimately controls a shop (a normal, unprivileged merchant/app-install) can trigger real Shopify webhooks for their own store, giving them a body + a valid HMAC signature pair computed with the app's shared secret over that exact body. Because the HMAC only signs `@raw_body` and never binds the `shop-domain` (or `topic`) headers, that same attacker can resend the webhook to the app's endpoint with the `shop-domain` header rewritten to any other installed shop (e.g. a victim tenant). `Utils::HmacValidator.validate` will still return `true` because it only re-derives the signature from the body [6](#0-5) , and `Registry.process` will hand the handler `WebhookMetadata` claiming the victim's `shop` [7](#0-6) .

### Impact Explanation
This is a cross-tenant access vector: a host application that keys any lookup, cache invalidation, data write, or session retrieval off `WebhookMetadata#shop` will perform that action against the wrong (victim) tenant's data using attacker-supplied body content, because the gem itself vouches for `request.shop` once `HmacValidator.validate` passes.

### Likelihood Explanation
Requires only an unprivileged actor who has installed the app on their own store (to obtain one valid signed body/HMAC pair) and the ability to POST directly to the app's public webhook endpoint with custom headers — no access to `api_secret_key`, tokens, or privileged accounts is needed.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` in the signable string (or otherwise authenticate them, e.g., via a signed URL/path segment that binds the shop) so `HmacValidator.validate` fails when any of those identity-bearing headers is altered.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and captures a real webhook delivery: body `B`, header `x-shopify-hmac-sha256: H` (valid because `H = HMAC_SHA256(secret, B)`).
2. Attacker POSTs to the app's webhook endpoint with body `B`, `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds since it hashes only `B`. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` to the handler, causing tenant-victim data to be created/updated/deleted using attacker-controlled content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
