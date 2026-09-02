### Title
Webhook HMAC only covers the request body, not the `shop-domain`/`topic`/`webhook-id` headers, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so `Utils::HmacValidator.validate` proves the body's authenticity but does not bind the `shop-domain`, `topic`, or `webhook-id` headers to that signature. `Registry.process` trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build `WebhookMetadata` and dispatch it to the host app's handler as the tenant identity for that payload.

### Finding Description
The identity binding that should hold is:
`shop-domain header used to attribute the webhook == shop-domain header covered by the verified HMAC`

In `lib/shopify_api/webhooks/request.rb`: [1](#0-0) 
`hmac` is read from the `hmac-sha256` header, `shop`/`topic`/`webhook_id` are read from separate headers, but `to_signable_string` returns only `@raw_body`.

`Utils::HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` treats a successful HMAC check as authorizing use of `request.shop`, `request.topic`, and `request.webhook_id` for building the metadata passed to the app's handler: [3](#0-2) 

Because the app-wide `api_secret_key` used to compute the HMAC is the same for every shop the app is installed on, any body+HMAC pair that Shopify genuinely delivered to the app for shop A (which an unprivileged attacker can obtain simply by installing the app on their own store and receiving a real webhook) remains a valid signature when the attacker replays it with the `shop-domain` header rewritten to shop B, and/or the `topic`/`webhook-id` headers changed. The verified bytes (body) and the bytes acted upon (shop identity, topic, webhook id) are not the same bytes — exactly the "bytes verified versus bytes parsed" pattern.

### Impact Explanation
This breaks the tenant boundary the whole webhook subsystem is built to preserve: `Registry.process` hands the host application a `WebhookMetadata` whose `shop` field is asserted to be authentic (because the HMAC "passed"), when in fact the shop attribution is attacker-controlled. Any Devin/host app that uses `data.shop` to route webhook data to the correct tenant record (the documented and expected use, per `docs/usage/webhooks.md`) can be made to apply attacker-supplied topic/body content to a victim shop's tenant, i.e. cross-tenant data injection/confusion — reachable by any user who can install the app on their own store and capture one legitimate webhook delivery.

### Likelihood Explanation
Requires no special privilege: standalone app installation (any unprivileged Shopify merchant/dev) is sufficient to obtain one valid `(raw_body, hmac)` pair, since the secret is shared across the whole app rather than being per-shop. Only header replay is required afterward.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material, e.g. compute the HMAC over the header values concatenated with the body, or validate that `request.shop` matches an app-known/expected value that was independently established (e.g. cross-checked against session storage) before trusting it in `Registry.process`. At minimum, document/enforce that `WebhookMetadata#shop` is not to be trusted as authenticated tenant identity without additional binding.

### Proof of Concept
1. Install the app on attacker-owned store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: headers include `x-shopify-hmac-sha256: <H>` and `x-shopify-shop-domain: attacker.myshopify.com`, with body `B`.
2. `H` was computed as `HMAC-SHA256(api_secret_key, B)` — this is verifiable via `lib/shopify_api/utils/hmac_validator.rb` lines 33-40, which hashes only the raw body.
3. Replay the exact same body `B` and hmac `H` to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/webhooks/registry.rb` line 190 succeeds (body unchanged), and `Registry.process` calls `handler.handle` with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, letting the attacker inject/forge webhook events attributed to `victim.myshopify.com`.

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
