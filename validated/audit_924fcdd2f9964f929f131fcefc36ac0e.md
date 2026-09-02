### Title
Webhook shop/topic/webhook-id headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, while the `shop`, `topic`, and `webhook_id` values used to route and process the event are taken from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `#hmac` is read from the `hmac-sha256` header: [1](#0-0) 

`Registry.process` verifies the request using only this body-derived HMAC, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` — all pulled from separate, unsigned headers — to build the `WebhookMetadata` dispatched to the app's handler: [2](#0-1) 

The identity binding that should hold is: `shop header == shop that produced/authorized this body`. Because the HMAC computation excludes the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header entirely, that equality is never checked — only `HMAC(body, secret) == received_hmac` is checked, which is independent of which shop's header accompanies the body.

This mirrors the report's bug class: a field that is acted upon (`shop`, used to key/route the webhook to a specific tenant's data) is not covered by the authentication mechanism (the HMAC), while another field (the body) is. Concretely, anyone who has previously observed one legitimate `(raw_body, hmac)` pair addressed to their own shop (e.g., a merchant who installed the app and received a genuine webhook for their own store) can resend that same body/HMAC pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a different (victim) shop's domain. `HmacValidator.validate` will still succeed because it only checks the body: [3](#0-2) 

The app's handler will then process attacker-controlled body content under the identity of the spoofed victim shop.

### Impact Explanation
This breaks the tenant boundary the webhook mechanism is supposed to enforce: an app that persists or acts on webhook data keyed by `WebhookMetadata#shop` can be made to apply another shop's genuine event data (or a stale/replayed event) to a victim tenant's records, since the `shop` claim is never cryptographically bound to the payload. This is a cross-tenant integrity issue reachable without possession of `api_secret_key` or any credential — only a previously-observed legitimate webhook delivery to the attacker's own store.

### Likelihood Explanation
Moderate: it requires the attacker to have received at least one legitimate webhook (trivial for anyone who installs the app on a store they control) and requires the host application to trust `WebhookMetadata#shop` for tenant-scoped actions — a very common usage pattern this gem itself sets up via `Registry.process`'s handler dispatch.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the signed material verified against the HMAC (or otherwise cryptographically bind them, e.g. by requiring the caller to independently confirm the delivering shop has an active session/webhook subscription id previously registered by this app) before dispatching to the handler in `Registry.process`.

### Proof of Concept
1. App has webhook processing enabled and a handler that updates a "Shop" record keyed by `WebhookMetadata#shop`.
2. Attacker installs the app on their own store `attacker.myshopify.com` and captures a genuine webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `HMAC(secret, B) == H`).
3. Attacker POSTs to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid), but `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` returns `true` (it only checks `B`/`H`), `Registry.process` builds `WebhookMetadata` with `shop: "victim.myshopify.com"` and body `B`, and the handler processes it as a genuine event for `victim.myshopify.com`.

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
