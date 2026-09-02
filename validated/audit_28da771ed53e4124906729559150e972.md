Confirmed the root cause: `Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `api_version`, and `webhook_id` are read from unauthenticated HTTP headers and are not part of the signed data.### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are trusted from unauthenticated headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed by `Utils::HmacValidator.validate` in `Registry#process` authenticates the body bytes but never binds them to the `shop`, `topic`, `webhook_id`, or `api_version` values, which are all read from plain HTTP headers. This is the same class of bug as the reported issue: a value that is acted upon by application logic (`vaultRewardsPerWeight`/here, tenant attribution) is not covered by the integrity check that is supposed to authenticate the whole message.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`, exposing `hmac` and `to_signable_string`: [1](#0-0) 

`to_signable_string` returns `@raw_body` only. Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) without any cryptographic binding: [2](#0-1) 

`Registry#process` validates the HMAC (which only proves the *body* bytes came from Shopify using the app's `client_secret`-derived signature), then immediately trusts `request.topic` to look up a handler and trusts `request.shop` to construct `WebhookMetadata`, which is handed to the app's `WebhookHandler#handle`: [3](#0-2) 

`WebhookMetadata.shop` is a `T::Struct` field consumed by the app-level handler as the tenant identifier for the event: [4](#0-3) 

The equality the code implicitly (and incorrectly) assumes is:
`shop header value == shop that produced/authorized raw_body`

But the HMAC only proves:
`hmac == HMAC_SHA256(client_secret, raw_body)`

Since `shop` (and `topic`/`webhook_id`/`api_version`) are excluded from `to_signable_string`, nothing prevents these header values from being swapped for a different value while keeping a valid `(raw_body, hmac)` pair.

### Impact Explanation
Any unprivileged internet user who has legitimately received one authentic webhook delivery for their own shop (e.g., an app installed on a store they control, or a captured/leaked webhook payload) can replay the same `raw_body` + `hmac` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) with an arbitrary victim shop domain or a different topic. `HmacValidator.validate` will still return `true` because it only checks the body, and `Registry#process` will dispatch the body's data to the app's handler tagged with the attacker-chosen `shop`. If the host application uses `WebhookMetadata#shop` to select which tenant's database row/records to write, update, or delete (a common and documented usage pattern), this results in cross-tenant data corruption/injection - e.g., attributing an `orders/create`, `customers/data_request`, `app/uninstalled`, or `shop/redact` payload to a shop that never sent it. This matches the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Likelihood is credible but not trivial: the attacker needs at least one legitimately-signed `(raw_body, hmac)` pair, which they can obtain by installing the app on a shop they control (a normal, unprivileged action) and capturing the webhook Shopify sends them, or from any other legitimately delivered webhook with predictable/attacker-controllable body content (e.g., an event that includes attacker-supplied data such as a customer/product they created). No access to `api_secret_key`, tokens, or TLS interception is required — only observation of one's own outbound webhook traffic and the ability to POST to the app's public webhook endpoint with modified headers.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string (or otherwise cryptographically bind them, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes all identity-relevant fields), so that `HmacValidator.validate` fails if any of these header values are altered relative to what Shopify actually signed. At minimum, `shop` must be covered since it is the tenant-identifying field consumed by `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and configures a webhook subscription (or triggers any topic with attacker-controlled body content, e.g., `customers/data_request` on their own store).
2. Shopify sends a legitimate webhook POST to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: <topic>`, `X-Shopify-Hmac-Sha256: <valid hmac of raw_body>`, and body `raw_body`.
3. Attacker captures this request and replays it to the same endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and/or `X-Shopify-Topic`).
4. `Registry#process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(client_secret, raw_body)` — unchanged, since `raw_body` wasn't modified — and passes validation: [5](#0-4) 
5. `WebhookMetadata.new(shop: request.shop, ...)` is built using the attacker-supplied `victim-shop.myshopify.com`, and passed to the app's `handler.handle`, causing the application to process the attacker's webhook body as if it originated from the victim shop.

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
