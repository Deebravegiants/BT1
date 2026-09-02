### Title
Webhook `shop`/`topic` headers are trusted for tenant routing despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` computes the HMAC over the raw body only, while the `shop` and `topic` values used by `Registry.process` to route and tag the webhook are pulled from unauthenticated HTTP headers. This breaks the binding "shop verified by HMAC == shop used as tenant identity," letting an unprivileged internet user replay a previously observed valid `(raw_body, hmac)` pair with forged `x-shopify-shop-domain`/`x-shopify-topic` headers and have it accepted as if it came from an arbitrary shop.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing the HMAC over `to_signable_string` and comparing it to the supplied `hmac`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers that are never part of the signed payload: [3](#0-2) 

`Registry.process` validates the HMAC once and then immediately trusts `request.topic` and `request.shop` for handler dispatch and for the data passed to the application's handler, treating the whole request as authenticated even though only the body bytes were actually verified: [4](#0-3) 

The check ("is this HMAC valid") answers a narrower question ("is this body byte-for-byte what the secret signed") than what the caller relies on ("is this shop/topic combination authentic"), exactly the "bytes verified versus bytes parsed/acted on" identity-binding gap called out in scope.

### Impact Explanation
Because `shop` is not bound to the signature, an attacker who has ever observed one legitimate `(raw_body, hmac)` pair delivered to the app's public webhook endpoint (e.g. from their own trial/store installation of the target app) can resend that exact body and HMAC to the same endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for an arbitrary victim shop domain. `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` will invoke the application's webhook handler with `WebhookMetadata#shop` set to the attacker-chosen shop. Any host application that uses `shop` from this metadata to attribute data, update per-tenant records, or make trust decisions ends up processing forged data under an incorrect tenant identity — a cross-tenant confusion that meets the Critical bar (cross-tenant access) without requiring the app's `client_secret`, an access token, or TLS interception.

### Likelihood Explanation
Exploitation only requires: (1) obtaining one valid `(body, hmac)` pair — trivially available to any developer who installs/trials the app on their own store and captures the resulting webhook POST, and (2) sending a normal unauthenticated HTTP POST to the app's public webhook route with modified headers. No secrets, tokens, or privileged access are needed, making this reachable by any unprivileged internet user who can install the target app once.

### Recommendation
Include the security-relevant routing fields (at minimum `shop-domain`, ideally `topic`) in the signed material used for validation, or independently authenticate the shop identity (e.g., cross-check `request.shop` against the shop associated with the session/webhook registration that the app expects) before trusting it in `WebhookMetadata`. At minimum, document clearly that `Registry.process`'s HMAC check does not authenticate `request.shop`/`request.topic`, so consuming applications do not implicitly rely on them being verified.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store, triggering a real webhook delivery to the app's public endpoint; attacker captures the raw POST body and the `x-shopify-hmac-sha256` value from that delivery.
2. Attacker sends a new HTTP POST to the same public webhook endpoint, using the identical captured body and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and succeeds.
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: ...)`, and the host application processes/attributes this forged event as belonging to `victim-shop.myshopify.com`, even though it never actually received data from that shop.

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
