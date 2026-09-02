## Title
Webhook shop and topic identity are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook by HMAC-validating only the raw request body, then hands the handler a `shop` and `topic` that are read straight from HTTP headers that are never included in that signature. Any party who can produce one HMAC-valid webhook body/signature pair (e.g. Shopify itself, sent to that attacker's own shop) can replay it with an arbitrary `shopify-shop-domain` header, and the app will process it as if it came from a different, victim tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled from HTTP headers that are not part of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` accepts the request as authentic once that body-only HMAC passes, then dispatches the handler using the unauthenticated `shop`/`topic` header values: [4](#0-3) 

This breaks the identity binding: `hmac-authenticated shop == shop delivered to handler` does not hold, because the HMAC binds nothing about which shop or topic the payload belongs to — only the body bytes. Contrast this with `Auth::Oauth::AuthQuery#to_signable_string`, which correctly folds `shop` and `host` into the signed string: [5](#0-4) 

Since the api secret key is shared across all shops/installs of a given app, an attacker who is a merchant on shop A (or who otherwise can trigger/capture one legitimate Shopify webhook delivery for topic T with a small/predictable body, e.g. `app/uninstalled` or a webhook whose body is empty/`{}`) obtains a body+HMAC pair that is valid for that api_secret_key regardless of which shop it's claimed to be from. The attacker replays that exact body and HMAC header to the app's webhook endpoint while setting `shopify-shop-domain` (or `x-shopify-shop-domain`) to a victim shop's domain and/or a different `shopify-topic`. `HmacValidator.validate` still passes (it never looks at those headers), and the handler is invoked believing the event genuinely originated from the victim shop/topic.

### Impact Explanation
This allows cross-tenant confusion at the application layer: a handler that looks up a merchant record by `WebhookMetadata#shop` (data.shop) can be made to act on the wrong tenant's session/state (e.g. trigger uninstall cleanup, cache invalidation, or business logic tied to shop identity) using an attacker-chosen shop value, without possessing that shop's real webhook traffic. This matches the "cross-tenant access" Critical-impact category since the shop identity binding that the host app relies on for tenant isolation is not actually enforced by this gem.

### Likelihood Explanation
Exploitation requires the attacker to obtain one authentic HMAC/body pair from Shopify (trivial if the attacker installs the app on their own shop, since Shopify signs every real webhook delivered to that install with the same shared `api_secret_key`), and then replay it against the app's public webhook endpoint with modified `shop`/`topic` headers. No secret material needs to be stolen — only the ability to receive one legitimate webhook, which any installer of the app already has.

### Recommendation
Include the identity fields the application will trust (`shop`, `topic`, and ideally `webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind them to the payload (e.g. verify `shop`/`topic` from the header against values embedded in/derivable from the signed body) before dispatching to the handler, so `Registry.process` cannot be tricked into associating a validly-signed body with an attacker-chosen shop or topic.

### Proof of Concept
1. App installs on attacker-controlled shop `attacker.myshopify.com`; Shopify delivers a real webhook, e.g. `app/uninstalled` with body `{}`, headers including `x-shopify-hmac-sha256: <H>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the identical raw body `{}` and `x-shopify-hmac-sha256: <H>` to the same webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` (and/or a different `x-shopify-topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over the body `{}` — validation succeeds. The handler is invoked with `WebhookMetadata(shop: "victim.myshopify.com", topic: ..., ...)`, as shown in [4](#0-3) , letting the attacker trigger shop-scoped logic under a victim's identity.

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
