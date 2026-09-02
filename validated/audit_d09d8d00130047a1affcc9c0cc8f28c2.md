Confirmed contrast: `AuthQuery#to_signable_string` (`lib/shopify_api/auth/oauth/auth_query.rb:33-43`) binds `shop` into the HMAC-signed string, but `Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) signs only `@raw_body`, leaving `shop`, `topic`, and `webhook_id` headers completely outside the HMAC. This is the identity-binding break I need.

### Title
Webhook `shop`/`topic` headers are not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC over the raw body only, while the `shop-domain`, `topic`, and `webhook-id` headers — which the registry hands to the host app's handler as the authenticated tenant/topic identity — are never included in the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` against the received `hmac`, i.e. it only proves the body bytes were signed by Shopify with the app's secret; it says nothing about which shop or topic that body was signed for: [2](#0-1) 

`Registry.process` then trusts `request.shop` and `request.topic` — both read straight from unauthenticated headers — to select the handler and to build the `WebhookMetadata` passed to the app's business logic: [3](#0-2) [4](#0-3) 

Compare this to the OAuth callback path, where `AuthQuery#to_signable_string` explicitly binds `shop` (along with `code`, `host`, `state`, `timestamp`) into the signed string before HMAC verification: [5](#0-4) 

The webhook path breaks the equality that should hold: `shop header verified by HMAC == shop identity acted on by the handler`. Any attacker who has received one genuinely-signed webhook body+HMAC pair (e.g., an unprivileged developer who installs the app on their own store and receives real, correctly-signed webhooks) can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting a different `shop-domain` (and/or `topic`) header value. `HmacValidator.validate` will still return `true` because it only checks the body bytes against the secret, so `Registry.process` will dispatch the attacker-chosen body to the handler under the identity of a shop the attacker does not control.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the library hands the host app a `WebhookMetadata#shop` value that it advertises as verified ("Invalid webhook HMAC" is the only check performed) but which is not cryptographically bound to the payload. Any host application that uses `data.shop` from a processed webhook to look up or mutate per-tenant state (the documented and expected usage per `docs/usage/webhooks.md`) can be made to attribute an attacker-controlled event body to a victim shop, or to misroute a body to the wrong topic handler. This matches the Critical category of cross-tenant access.

### Likelihood Explanation
The prerequisite is just having received a single legitimately-signed webhook from Shopify for any shop the attacker controls (trivial for anyone who can install a free/dev app), then replaying it with a modified header value — no access to `api_secret_key`, no token theft, and no privileged account needed. This is straightforward for any unprivileged internet user who is a merchant/developer of their own store.

### Recommendation
Include the `topic`, `shop-domain`, and `webhook-id` header values in the signable string (or otherwise cryptographically bind them, e.g. compute the HMAC over `"#{topic}\n#{shop}\n#{webhook_id}\n#{raw_body}"`) so `Utils::HmacValidator.validate` fails when any of these identity-bearing fields are altered, mirroring how `AuthQuery` binds `shop` in the OAuth callback flow.

### Proof of Concept
1. Register the app on attacker-owned shop `attacker.myshopify.com` and subscribe to `orders/create`.
2. Trigger an order event; capture the genuine webhook POST, including its exact `raw_body` and the `x-shopify-hmac-sha256` header (a valid signature over that body using the app's real secret).
3. Replay this POST to the app's webhook endpoint, keeping `raw_body` and `hmac` header unchanged, but set `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally alter `x-shopify-topic`).
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks `raw_body` against the secret.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: ..., body: attacker_body)`, causing the host app to process attacker-controlled data as if it originated from `victim-shop`.

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
