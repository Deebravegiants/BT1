### Title
Webhook `shop-domain` (and `topic`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body. The `shop-domain` and `topic` values that the app uses to determine *which tenant* the payload belongs to and *which handler* processes it are taken from HTTP headers that are never included in the signed material. Because the app's `api_secret_key` is shared across all shops that install the app (it is not shop-specific), any actor who can obtain one valid `(raw_body, hmac)` pair for their own shop installation can replay that pair with a different `shop-domain` header to make the app process it as if it came from another shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers that are excluded from the signed string: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string` (i.e., only the body) against the shared `Context.api_secret_key`: [3](#0-2) 

`Registry.process` trusts `request.shop` and `request.topic` (unsigned headers) to route the webhook and populate `WebhookMetadata` once the (body-only) HMAC check passes: [4](#0-3) 

The broken identity binding is:

`hmac_valid(raw_body, api_secret_key) == true` is treated as proof that `request.shop == "the shop that actually sent this payload"`, but the equality that is actually enforced is only `hmac_valid(raw_body, api_secret_key) == true`, which is a property of the **app's shared secret**, not of any particular shop. Since `api_secret_key` is identical for every shop that has installed the app, any shop-A merchant can capture a legitimately-signed `(raw_body, hmac)` pair for a webhook fired by their own store, then replay that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) header for shop B. `HmacValidator.validate` will still succeed because it only checks the body against the shared secret, and `Registry.process` will hand the payload to the handler tagged with the attacker-chosen `shop`.

### Impact Explanation
This crosses a tenant boundary: an unprivileged holder of a legitimate installation for Shop A can make the merchant application believe/act on webhook data as if it originated from Shop B, without ever needing Shop B's credentials, access token, or secret. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up/attribute orders, update per-shop state, or trigger side effects keyed by shop), this enables cross-tenant data confusion/injection — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The attacker only needs: (1) their own legitimate installation of the target app on any shop (something any merchant can obtain by installing a public/free app), and (2) the ability to trigger a webhook event and capture the raw body/HMAC Shopify sends for their own shop, and (3) the ability to POST arbitrary headers to the app's public webhook endpoint. No secrets, tokens, or privileged access from the victim shop are required, making this practically exploitable by any unprivileged internet user who is a customer/merchant of the same app.

### Recommendation
Include the identity-relevant fields (`shop-domain`, `topic`, `webhook_id`, `api-version`) in the material that is authenticated, or otherwise cryptographically bind the header values to the signed body (e.g., verify that the HMAC-signed body itself encodes/matches the shop it claims to be for, or require Shopify's per-shop signing where available). At minimum, document that consumers of `ShopifyAPI::Webhooks::Registry.process` must independently confirm that `request.shop` corresponds to a shop with an active session/installation before trusting the payload, and reject requests whose body's declared identity does not match the header-derived shop.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged action).
2. Attacker triggers any subscribed webhook topic (e.g., `orders/create`) on their own shop and captures the raw POST: headers `X-Shopify-Hmac-Sha256: <hmac>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`, and body `raw_body`.
3. Attacker replays the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only (`Request#to_signable_string`) and it matches, so `Registry.process` proceeds and invokes the handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, even though the payload never originated from `victim-shop.myshopify.com`. [4](#0-3) [1](#0-0)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
