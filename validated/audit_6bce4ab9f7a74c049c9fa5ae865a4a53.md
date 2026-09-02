### Title
Webhook HMAC does not bind the `shop-domain` header, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw request body only, never incorporating the `shopify-shop-domain` header. `Webhooks::Registry.process` trusts `request.shop` unconditionally after validating only the body's HMAC, so the shop attribution of an otherwise validly-signed webhook can be forged by anyone who can replay a legitimately-signed payload with a different `shop-domain` header.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it to the supplied `hmac` value: [1](#0-0) 

For webhooks, `Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

But `shop` is read straight from an HTTP header that is completely outside the signed content: [3](#0-2) 

`Registry.process` only checks the body HMAC before dispatching to the handler with the (unauthenticated) `request.shop` value: [4](#0-3) 

The identity binding the code implicitly assumes is:
`hmac_valid(raw_body) == true` implies `shop-domain header == shop that produced raw_body`

But because `shop-domain` is never part of `to_signable_string`, this equality does not actually hold — the HMAC only proves "this body was signed with our `api_secret_key`", not "this body came from shop X". Any two webhook deliveries to the same app (across all installed shops, since they share one `api_secret_key`) that have byte-identical raw bodies produce byte-identical valid HMACs regardless of which shop header accompanies them.

### Impact Explanation
An unprivileged internet user who legitimately controls their own shop installation of the app can trigger a webhook delivery from Shopify containing a chosen/foreseeable raw body (e.g., a `products/create` or similar webhook whose payload they control via their own store data) with a validly-computed HMAC. Because the gem's `Registry.process` never binds that HMAC to the `shop-domain` header, the attacker can replay the exact `(raw_body, x-shopify-hmac-sha256)` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. `HmacValidator.validate` still returns `true` (the body signature is untouched), and the handler receives `WebhookMetadata` attributing that (attacker-controlled) payload to the victim shop: [5](#0-4) 

Depending on how the host app keys its per-tenant data store off `data.shop`, this can be used to inject or overwrite data under a victim tenant's account — a cross-tenant access/data-integrity break, meeting the Critical bar ("cross-tenant access").

### Likelihood Explanation
This requires only that the attacker operate their own instance of the app (a normal unprivileged merchant/install) and be able to intercept or predict one raw webhook body/HMAC pair for their own shop, then replay it with a forged header — no access to the app's `client_secret`/`api_secret_key`, access tokens, or any other privileged credential is required, and no TLS interception of the victim's traffic is needed since the attacker crafts and sends their own forged request directly to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and preferably `topic` and `webhook-id`) in the value that is HMAC-verified, e.g., have `Webhooks::Request#to_signable_string` incorporate `shop-domain`/`topic` alongside the raw body, or independently verify that the `shop-domain` header corresponds to a shop with a currently valid, stored session/access token before dispatching to handlers in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers an event (e.g. edits a product) causing Shopify to POST a webhook with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker intercepts this legitimate request to their own endpoint (they control the receiving server/logs).
3. Attacker replays a new POST to the same webhook endpoint with the identical body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only (`Request#to_signable_string`) — validation succeeds. [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host app to process attacker-controlled data as if it originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
