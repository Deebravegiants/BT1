## Title
Webhook shop/topic identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable material solely from the raw request body, while the `shop` and `topic` values used to route and attribute the webhook are read from unauthenticated HTTP headers. Because the same `api_secret_key` is shared across all shops that install the app, any actor who can obtain one genuine `(body, hmac)` pair for the shared secret can replay it to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header, and `Utils::HmacValidator.validate` will still accept it.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` and `Request#topic` are read directly from headers with no cryptographic binding to the signed payload: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` only: [3](#0-2) 

`Registry.process` trusts the header-derived `request.shop` and `request.topic` for dispatch and hands them straight to the app's handler once the (body-only) HMAC check passes: [4](#0-3) 

The identity binding that should hold is: `shop verified by HMAC == shop used for tenant attribution`. In this code, the equality actually enforced is `body bytes verified by HMAC == body bytes parsed`, while `shop`/`topic` are accepted from unauthenticated header bytes. Because `api_secret_key` (the HMAC key) is identical for every shop that installs a given app, a genuine `(raw_body, hmac)` pair captured from *any* installed shop remains valid regardless of which shop-domain header is attached to the replayed request.

### Impact Explanation
This breaks the shop-authentication boundary between tenants (Critical - cross-tenant access): an unprivileged actor who controls or observes webhook traffic for one shop that has installed the target app can forge a webhook that the app's handler will process as if it originated from a completely different (victim) shop, since `WebhookMetadata.shop` is populated straight from the unauthenticated header: [5](#0-4) 
Depending on how the host app keys its data/session lookups off `data.shop`, this can lead to cross-tenant data injection, corruption of another merchant's records, or triggering privileged app logic (e.g. uninstall/GDPR handlers) attributed to the wrong shop.

### Likelihood Explanation
Any developer or free-trial user can install the vulnerable app on their own shop, capture a legitimate webhook `(body, hmac)` pair for that app's shared `api_secret_key`, and replay it directly to the app's public webhook URL with a different `shop-domain` header. No access token, `client_secret`, or privileged account is required — only a normal installation of the target app, which is achievable by any internet user for public apps.

### Recommendation
Include `shop` (and ideally `topic`) in the signable string that is HMAC-verified, or independently verify the header-derived shop against a value embedded in and covered by the signed payload before using it for tenant attribution. At minimum, `Registry.process` should require that the shop from the header matches the shop associated with the session/handler being invoked, rather than trusting the header value used for the HMAC-blind dispatch.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`; trigger a genuine webhook (e.g. `orders/create`) and capture the raw POST: `raw_body` and header `X-Shopify-Hmac-Sha256`.
2. Resend the exact same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's public webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim.myshopify.com` (a shop that also has the app installed).
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the signature from `raw_body` only and succeeds, since the secret is shared across shops.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the handler with `shop: "victim.myshopify.com"` and the attacker-controlled body, even though that data never came from the victim shop.

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
