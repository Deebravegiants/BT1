### Title
Webhook HMAC covers only the request body, not the `shop-domain`/`topic` headers used to route and attribute the event, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the body bytes but never binds the `x-shopify-shop-domain` or `x-shopify-topic` headers to the signature. `Registry.process` then uses these unauthenticated headers to select the handler and to construct `WebhookMetadata` (`shop:`, `topic:`) that the app's handler trusts as the tenant identity for the event.

### Finding Description
The HMAC validation performed in `Utils::HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received `hmac`. [1](#0-0) 

For webhook requests, `to_signable_string` is defined as just the raw body: [2](#0-1) 

The `shop` and `topic` accessors, however, are derived purely from HTTP headers that are not part of the signed content: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately dispatches based on `request.topic`, and hands the handler `request.shop` as the tenant identity, without any check binding `shop`/`topic` to the signed body: [4](#0-3) 

The identity binding that should hold is:
`hmac == HMAC(secret, body || shop || topic)`

but the actual implementation only enforces:
`hmac == HMAC(secret, body)`

This is exactly the bug class from the report: a field that is *acted upon* (here, `shop`/`topic`, used for tenant routing and attribution) is not included in the cryptographically verified value (the HMAC), analogous to `VerifyVoteExtension()` not binding `BlockHeader` into the signed `AttestationRoot`.

Because a single `api_secret_key` is shared by the app across all its installed shops, any ordinary merchant who installs the app on their own store (an unprivileged action, requiring no leaked credentials) can capture a legitimately-signed `(body, hmac)` pair from a real webhook delivery (e.g., `app/uninstalled` with body `{}`, or any webhook whose body content is shop-agnostic). They can then replay that exact `(body, hmac)` pair directly to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and/or `x-shopify-topic`) with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will invoke the handler believing the event originates from, and pertains to, the victim shop.

### Impact Explanation
This breaks the tenant isolation boundary: an attacker who is a legitimate (but unprivileged) merchant of the app can forge webhook events that are processed as belonging to a different, victim tenant. Depending on the app's webhook handlers (e.g., `app/uninstalled` clearing a shop's stored session/access token, or handlers that write data keyed by `shop`), this can lead to cross-tenant data corruption, forced session/token invalidation for another merchant, or injection of attacker-controlled data attributed to a victim's store — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. No leaked credentials, TLS interception, or privileged access is required — only the ability to install the app on one's own shop (a normal, unprivileged merchant capability) to obtain one valid `(body, hmac)` pair, plus the ability to send a direct HTTP POST to the app's public webhook endpoint with a different `shop-domain`/`topic` header. The HMAC verification logic as written in this gem provides no protection against this replay because it structurally never covers those header fields.

### Recommendation
Include the `shop` (and ideally `topic`) values in the signed/verified content, or otherwise cryptographically bind them to the signature check in `Utils::HmacValidator`/`Webhooks::Request`, e.g. by verifying `request.shop` and `request.topic` against a MAC that covers all three fields, not just the raw body. At minimum, document and enforce that `WebhookMetadata.shop`/`topic` must not be trusted for tenant attribution unless additionally corroborated (e.g., cross-checked against a known/registered shop for that webhook subscription).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, and triggers a `app/uninstalled` webhook (body `{}`), capturing the legitimate headers:
   - `x-shopify-topic: app/uninstalled`
   - `x-shopify-hmac-sha256: <valid HMAC of "{}">`
   - `x-shopify-shop-domain: attacker.myshopify.com`
2. Attacker sends a direct POST to the app's webhook endpoint with the same body `{}` and the same valid `x-shopify-hmac-sha256`, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds (body signature is valid) per `lib/shopify_api/utils/hmac_validator.rb`.
4. `Registry.process` dispatches to the `app/uninstalled` handler with `shop: "victim.myshopify.com"` per `lib/shopify_api/webhooks/registry.rb` lines 188-200, causing the app to act (e.g., delete/invalidate) on the victim's tenant data despite the request never having been authenticated for that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
