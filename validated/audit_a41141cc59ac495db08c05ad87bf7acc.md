## Finding

### Title
Webhook shop/topic attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing via signature replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` only verifies the HMAC over the raw request body, but the `shop` (and `topic`) values used to attribute the webhook to a tenant are read directly from unauthenticated HTTP headers that are never included in the signed payload. Anyone who can obtain one genuine, HMAC-signed webhook body (e.g., by installing the app on their own, free development store) can replay that exact body+HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and `shopify-topic`) header, and the gem will report it to the app's handler as data belonging to any shop the attacker chooses.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors, however, are derived purely from HTTP headers supplied with the request, with no cryptographic binding to the body that is HMAC-verified: [2](#0-1) 

`Registry.process` validates only this body-only HMAC via `Utils::HmacValidator.validate(request)`, and then immediately builds `WebhookMetadata` from the unauthenticated `request.shop` / `request.topic` header values and dispatches it to the registered handler: [3](#0-2) 

`HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string`, i.e. the raw body, and compares it with the `hmac-sha256` header: [4](#0-3) 

This breaks the identity binding: `shop attributed to webhook (request.shop header)` ≠ `shop the HMAC actually authenticates (nothing — only the body bytes)`. Because typical Shopify webhook payloads (e.g. `orders/create`, `products/update`) do not embed the originating shop's myshopify domain inside the JSON body, a valid `(body, hmac)` pair captured from one shop's legitimate webhook remains valid when replayed with a different `shopify-shop-domain` header. The gem's own documentation reinforces the false assumption that HMAC validation confirms provenance of the whole request ("This will verify the request did indeed come from Shopify"), while in fact only the body bytes are authenticated: [5](#0-4) 

### Impact Explanation
An attacker who has ever received one legitimate webhook from Shopify for any shop (trivially obtainable by installing a free public app or their own test app on a dev store) can forge webhook deliveries attributed to any other merchant by replaying the same signed body with a swapped `shop-domain` header. Since apps typically key business logic (order processing, inventory sync, billing, data storage) off `WebhookMetadata#shop`, this allows injecting attacker-controlled data into another tenant's data pipeline or corrupting per-shop state — a cross-tenant integrity/isolation violation reachable by an unprivileged internet user with no access token or `client_secret` required.

### Likelihood Explanation
Exploitation requires only: (1) a single genuine signed webhook body from Shopify (freely obtainable), and (2) the ability to POST to the target app's public webhook endpoint (any internet-reachable app router). No credentials, TLS interception, or insider access are needed, making this readily reachable by an unprivileged actor.

### Recommendation
Bind the `shop` (and `topic`) values into the HMAC-verified surface, e.g. by including these header values in the signable string used by `HmacValidator`, or by requiring applications/gem consumers to cross-check `request.shop` against an independently known/registered shop before trusting it. At minimum, update `to_signable_string` in `lib/shopify_api/webhooks/request.rb` to incorporate the shop and topic headers so that tampering with them invalidates the HMAC, and correct the documentation in `docs/usage/webhooks.md` to accurately describe what is and isn't authenticated.

### Proof of Concept
1. Install the target's app (or any Shopify app using this gem) on a free development store `attacker-shop.myshopify.com`.
2. Capture a legitimate webhook POST (e.g. `orders/create`) delivered to the app's callback URL, noting the raw body and `x-shopify-hmac-sha256` header.
3. Replay this exact request to the same (or a different) app instance's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally `x-shopify-topic` if compatible with the body schema).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which succeeds because it only checks the (unchanged) body against the (unchanged) HMAC — per `lib/shopify_api/utils/hmac_validator.rb:12-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` per `lib/shopify_api/webhooks/registry.rb:198-199`, causing the application to process attacker-supplied data as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
