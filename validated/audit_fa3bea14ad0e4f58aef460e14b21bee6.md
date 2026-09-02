I have enough to finalize the analog: the `x-shopify-shop-domain` header consumed by `ShopifyAPI::Webhooks::Request#shop` and passed through `Registry#process` to the handler is never covered by the HMAC signature, which is computed only over `@raw_body`.

### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that reads the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header, while `to_signable_string` (the value HMAC-verified by `Utils::HmacValidator`) returns only `@raw_body`. `Registry.process` verifies the HMAC and then forwards `request.shop` (and `topic`, `webhook_id`, `api_version`) straight into `WebhookMetadata`, unverified.

### Finding Description
`Registry.process` does:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [1](#0-0) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`: [2](#0-1) 

And `Request#to_signable_string` returns only the raw body, never the headers: [3](#0-2) 

So the equality the code actually enforces is:
`HMAC(secret, raw_body) == received_hmac`

but the identity binding the host application relies on for tenant separation is:
`shop_header == shop_that_produced(raw_body, hmac)`

These are two different things: the second is never checked anywhere in this gem. Any party that has legitimately received one authentic `(raw_body, hmac)` pair from Shopify for *their own* shop (e.g., an app developer's own test/dev store, or any merchant that has the app installed and can trigger a webhook with attacker-influenced body content, such as a webhook whose payload echoes merchant-controlled data) can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value for a *different* victim shop. `HmacValidator.validate` still passes because it only checks the body, and `WebhookMetadata.shop` will report the attacker-chosen victim shop to the host application's handler.

### Impact Explanation
Host applications built on this gem are documented to trust `data.shop` from `WebhookMetadata` as the tenant identifier for looking up/updating per-merchant records (per `docs/usage/webhooks.md`, `data.shop` is described as "The shop domain of the webhook" with no caveat that it is unauthenticated). Because the shop field crosses the HMAC trust boundary unverified, an attacker with a legitimately-signed webhook for their own store can cause the handler to process (and thus persist/act on) that content attributed to a different, victim shop, which is a cross-tenant integrity break — the app will believe data belongs to shop B when it was actually produced/signed for shop A.

### Likelihood Explanation
Exploitation requires only: (1) network access to the app's public webhook endpoint (unprivileged internet requirement satisfied), and (2) possession of one valid `(raw_body, hmac)` pair, which any merchant that has installed the app already has (e.g., from their own store's webhook deliveries, which they can trigger via ordinary store actions). No access to `api_secret_key` is needed to forge the header swap — only replay of an already-valid signed body with a different claimed shop.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the signed material that `Utils::HmacValidator` checks, e.g., include the `x-shopify-shop-domain` header in `to_signable_string`, or independently authenticate the shop domain against the caller's own webhook registration/session records before trusting `WebhookMetadata.shop` in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) with a body they control the content of.
2. Shopify delivers the webhook to the app's endpoint with a legitimate `x-shopify-hmac-sha256` computed over that exact `raw_body` using the app's `api_secret_key`, and header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the identical `raw_body` and `x-shopify-hmac-sha256` value to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds (it only checks `raw_body` against the HMAC) per [4](#0-3) , and `Registry.process` invokes the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` per [5](#0-4) , causing the host app to attribute attacker-controlled content to the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
