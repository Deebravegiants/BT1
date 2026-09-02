### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted for tenant/event dispatch but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The reorg-attack report is about `create`-deployed contract addresses being trusted for identity/ownership before the creation transaction is final, i.e. an "acted-upon" identifier that isn't actually bound by a strong, unforgeable commitment. The closest analog in this gem is `ShopifyAPI::Webhooks::Request`/`ShopifyAPI::Webhooks::Registry`, where the `shop-domain`, `topic`, and `webhook-id` headers are used to route and attribute an inbound webhook to a specific tenant/topic, but the HMAC signature verified by `Utils::HmacValidator` only covers the raw request body, not these header values.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates only this body HMAC and then dispatches the handler using the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` values: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e., the body) and the app's shared `api_secret_key`: [4](#0-3) 

The equality that the code implicitly assumes is:
`hmac_valid(body) == true` implies `request.shop / request.topic / request.webhook_id are trustworthy for this body`

but what's actually proven is only:
`HMAC_SHA256(api_secret_key, body) == received_signature`

The `shop`, `topic`, and `webhook_id` headers are never part of the signed material, so the binding "signature verifies ⇒ these headers describe the event that produced this body" does not hold.

### Impact Explanation
Because the `api_secret_key` is shared across every shop that installs the app (it's an app-level secret, not a per-shop secret), any merchant who has legitimately installed the app can receive a validly-signed webhook body for their own store (an unprivileged action requiring no special credentials). That merchant can then replay the same body + HMAC pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to name a different shop or topic. `Registry.process` will accept the forged headers as valid because the signature check never touched them, and the handler will be invoked with `WebhookMetadata` claiming to belong to another tenant/topic: [5](#0-4) 

Any host application that uses `request.shop` (or `topic`) from `WebhookMetadata` to key data writes, cache invalidation, subscription state, or GDPR/redact processing (`shop/redact`, `customers/redact`, `customers/data_request` are exactly the topics this gem hard-codes as mandatory) is exposed to cross-tenant data confusion driven entirely by an unprivileged installer of the app.

### Likelihood Explanation
Moderate. It requires the attacker to be a legitimate (but unprivileged, self-service) installer of the target app — trivial for any public Shopify app — and to control the raw HTTP request delivered to the app's webhook endpoint (also straightforward, since this is a plain HTTP POST target, not gated by TLS client auth or IP allow-listing in this gem). No access token, `api_secret_key`, or social engineering is needed; only the ability to receive one's own legitimately-signed webhook and replay it with modified identity headers.

### Recommendation
Include the tenant/event identity fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable material verified by `HmacValidator`, or otherwise cryptographically bind them to the body (e.g., verify `shop` against a shop that is known to be currently installed/registered for that specific webhook subscription before dispatch) rather than trusting header values that sit outside the HMAC's coverage.

### Proof of Concept
1. App AttackerCo installs the target Shopify app on `attacker-shop.myshopify.com` and registers a webhook for topic `orders/create`.
2. Shopify sends a webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(api_secret_key, B)` for shop `attacker-shop.myshopify.com`.
3. Attacker intercepts this legitimate request (they control their own inbound traffic/proxy) and replays it to the same app endpoint, keeping body `B` and the valid HMAC header, but rewriting `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and/or `x-shopify-topic` to `shop/redact` or another mandatory topic).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only and succeeds, since the body and signature are unchanged: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, causing the host application to process attacker-controlled webhook content under the victim's tenant identity.

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
