### Title
Webhook `shop` (and `topic`) header is trusted for tenant identity but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC signature validated by `HmacValidator` binds the *body* to the app's secret but does **not** bind the `shop-domain` (or `topic`) headers. `Registry.process` nonetheless uses `request.shop` (and `request.topic`) taken straight from these unauthenticated headers as the tenant identity forwarded to the app's webhook handler. This breaks the intended equality `hmac_signed_bytes == identity_bytes_trusted_by_handler`.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`, never the `shop`, `topic`, or `webhook_id` headers. `HmacValidator.validate` computes the HMAC over `to_signable_string` and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` then does the HMAC check and, on success, unconditionally trusts `request.shop` and `request.topic` (sourced from headers, not from the signed payload) to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the app's `client_secret`/HMAC key is shared across every shop that installs the app (it is the *app's* secret, not a per-shop secret), any merchant that installs the app can trigger a real webhook delivery to their own store, capture the resulting `(raw_body, hmac)` pair from a genuine Shopify-signed request, and then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (and/or `shopify-topic` header) naming a different, victim shop. The HMAC check in `HmacValidator.validate` still succeeds, because it only ever verifies the body bytes, not the shop or topic. `Registry.process` will then pass the forged `shop` value straight to the app's `handler.handle` call as if the event genuinely originated from the victim tenant.

This is precisely the "field acted on but not covered by the HMAC" identity-binding break: the binding the app relies on is `signed_bytes == (body)`, but the identity actually used by the handler is `(shop, topic, body)`. `shop` and `topic` are unauthenticated inputs.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` (or `#topic`) returned by `Registry.process`/`handler.handle` to select which tenant's data to update, look up, or overwrite is exposed to cross-tenant data injection/manipulation: an attacker who is merely a legitimate account holder for their own shop can forge webhook deliveries that the host application will process under a different, unrelated shop's identity. This satisfies the Critical "cross-tenant access" impact category, since no credential belonging to the victim tenant or the app's `client_secret` is required by the attacker — only their own legitimate access to trigger real webhooks for their own store and the ability to send arbitrary HTTP requests to the app's public webhook endpoint.

### Likelihood Explanation
Likelihood is moderate to high in any real deployment: the webhook endpoint is a public HTTP endpoint by design (Shopify calls it over the internet), the attacker does not need any secret (they only need a genuine `(body, hmac)` pair from any topic they can trigger on their own installed shop, which is trivial for a self-serve merchant), and nothing in `Request`, `HmacValidator`, or `Registry` prevents the header substitution.

### Recommendation
Include the `shop-domain` and `topic` values in the signed material that is verified, or independently validate that the `shop-domain` header corresponds to a shop actually authorized/installed for that app before trusting it as tenant identity. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and must not be trusted as tenant identifiers without an additional binding check (e.g., cross-referencing against a known/installed shop list, or verifying the `shop` value is consistent with data embedded in the (currently unsigned) body when available).

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers any webhook topic the app subscribes to, e.g. `orders/create`.
2. Attacker captures the real request Shopify sends, including body `raw_body` and header `x-shopify-hmac-sha256` (valid HMAC over `raw_body` using the app's shared `client_secret`).
3. Attacker resends this exact `(raw_body, hmac)` to the app's webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic:` (optionally a different registered topic)
4. `ShopifyAPI::Webhooks::Request.new` parses headers; `HmacValidator.validate` succeeds because it only hashes `raw_body`, unaffected by the header changes (`lib/shopify_api/webhooks/request.rb` lines 35-38, `lib/shopify_api/utils/hmac_validator.rb` lines 26-31).
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: attacker_controlled_body, ...)` (`lib/shopify_api/webhooks/registry.rb` lines 188-200), causing the host application to process attacker-controlled data under the victim shop's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
