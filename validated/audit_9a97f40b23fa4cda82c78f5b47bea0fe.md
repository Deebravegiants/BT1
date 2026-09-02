## Title
Webhook `shop` (and `topic`/`webhook_id`) identity is authenticated by header, not bound by HMAC, allowing cross-tenant webhook replay/forgery - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop`, `topic`, and `webhook_id` values that the gem forwards to the merchant's application handler are read directly from unauthenticated HTTP headers. `HmacValidator.validate` only certifies the integrity of `@raw_body` against `Context.api_secret_key`; it never binds that signature to the `shop-domain` header value that `Registry.process` subsequently trusts as the tenant identity.

## Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

Note `to_signable_string` returns `@raw_body` only, line 37. The `shop`, `topic`, and `webhook_id` accessors read straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates only the body signature, then unconditionally forwards the header-derived `request.shop`, `request.topic`, and `request.webhook_id` to the app's handler as trusted tenant metadata: [3](#0-2) 

`WebhookMetadata` exposes `shop` as a plain, unauthenticated `String` field that the documented handler pattern uses directly to key the tenant scope (`shop_domain: data.shop`): [4](#0-3) [5](#0-4) 

**Identity binding broken as an equality:** the value certified by the HMAC (`HMAC(raw_body, api_secret_key) == received_hmac`) is not equal to the value used to select tenant context (`shop-domain` header). The library's HMAC check verifies "this body byte-string was produced by Shopify with our secret," but `Registry.process`/`WebhookMetadata` treats the separate, unsigned `shop-domain` header as if it had the same guarantee.

Concretely: any unprivileged user who owns a Shopify store and has installed the target app can trigger a real webhook delivery for their own shop (e.g., `orders/create`), producing a body + valid HMAC signature for topic `T` and payload `P`. That request/response pair (raw body + `X-Shopify-Hmac-Sha256`) travels to the app's public webhook endpoint. Because the signature covers only `@raw_body` and never the `shop-domain`, `topic`, or `webhook-id` headers, the same body+HMAC pair remains valid if replayed with a forged `X-Shopify-Shop-Domain` (or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header naming a different, victim shop. `HmacValidator.validate` (called from `Registry.process`) will still return `true` because it only recomputes and compares against `@raw_body`: [6](#0-5) 

The app then processes attacker-controlled data as authentic content belonging to the victim tenant, because the gem hands the header-derived `shop` straight through as trustworthy in `WebhookMetadata`.

## Impact Explanation
This crosses a tenant boundary without any credential belonging to the victim shop: an attacker who only controls their own (unprivileged) shop's webhook traffic can cause an app built on this gem to attribute webhook data to an arbitrary other shop domain. Depending on how the host app uses `data.shop` (as documented, e.g., to select the tenant DB record or session for background processing), this enables cross-tenant data injection/impersonation — matching the "cross-tenant access" Critical impact category.

## Likelihood Explanation
Likelihood is bounded by the fact that this is a well-known, inherent property of Shopify's own webhook signing scheme (the platform signs only the request body, not delivery headers) — it is not unique misuse by this gem, and exploitation additionally requires an internet-reachable webhook endpoint and a host app that keys tenant-scoped logic off `data.shop`/`data.topic` without independent verification (e.g., checking the shop against an app-installation record before trusting the payload). The gem does not document this header/body binding gap or warn integrators that `shop` is unauthenticated, so a straightforward implementation following `docs/usage/webhooks.md` (`shop_domain: data.shop`) is directly exposed.

## Recommendation
- Document explicitly in `docs/usage/webhooks.md` and on `WebhookMetadata`/`Request#shop` that `shop`, `topic`, and `webhook_id` are **not** covered by the HMAC signature and must be independently corroborated (e.g., matched against a known installed-shop record) before being used for tenant-scoped side effects.
- Where feasible, have `Registry.process` cross-check the `shop-domain` header against the shop embedded in the parsed webhook body (most Shopify webhook payloads include shop-identifying fields) and reject mismatches.
- Consider exposing a stricter verification mode that binds headers into the signable string comparison at the app layer, or surfacing a warning when `shop` cannot be corroborated.

## Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a real webhook (e.g., creates an order), causing Shopify to POST a body `B` with a valid `X-Shopify-Hmac-Sha256` header to the app's public webhook endpoint `POST /webhooks`.
2. Attacker captures `B` and the valid HMAC value `H` (trivial since it is their own webhook traffic, requiring no special access).
3. Attacker replays the exact same request to the same endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` while keeping body `B` and HMAC `H` unchanged.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` → passes.
5. `Registry.process` invokes the app handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: request.topic, body: parsed_body, ...)`, causing the app to process attacker-supplied data as though it originated from `victim.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-30)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
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
