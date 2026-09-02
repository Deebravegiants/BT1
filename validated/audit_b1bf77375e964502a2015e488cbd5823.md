This confirms the finding. `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` [1](#0-0) , but the HMAC signature only ever covers `@raw_body` [2](#0-1) . The `shop`, `topic`, and `webhook_id` values that are handed to the application's webhook handler as the tenant/topic identity are read straight from HTTP headers and are never part of the signed content [3](#0-2) .

### Title
Webhook shop/topic identity not covered by HMAC allows cross-tenant webhook confusion - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns `@raw_body`, so the HMAC computed over `X-Shopify-Hmac-Sha256` authenticates the request body bytes only. The `shop-domain`, `topic`, and `webhook-id` headers, which `Registry.process` uses to route the payload and populate `WebhookMetadata` (the tenant identity the app acts on), are read from unauthenticated headers.

### Finding Description
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` accessor [4](#0-3) . For webhooks, `to_signable_string` is defined as just `@raw_body` [2](#0-1) . Meanwhile `shop`, `topic`, and `webhook_id` are derived purely from HTTP headers with no cryptographic binding to the signature [5](#0-4) .

`Registry.process` trusts `request.topic` to select the handler and trusts `request.shop` to stamp the `WebhookMetadata` passed to the app's handler, after only checking the body HMAC [1](#0-0) . The identity binding the gem should enforce is: `hmac == HMAC(secret, shop || topic || body)`, but the actual check is `hmac == HMAC(secret, body)` while `shop`/`topic` are taken from unauthenticated bytes. Any request bearing a previously-observed valid `(body, hmac)` pair — trivial to obtain since many webhook bodies are `{}` or highly predictable/repeating across shops and topics that share a payload shape — can be replayed with attacker-chosen `shop-domain`/`topic` headers and will pass `HmacValidator.validate`.

### Impact Explanation
This breaks the tenant/topic identity binding: an app that dispatches per-shop side effects (e.g. data deletion for `customers/redact`, cache invalidation, provisioning) keyed off `request.shop`/`request.topic` can be made to act on behalf of a different shop than the one whose secret-signed traffic produced the HMAC, since the header values carrying that identity are never covered by the signature. This is a cross-tenant identity-confusion vector reachable by any unprivileged internet user who can send an HTTP POST to the app's webhook endpoint with a body/HMAC pair they've observed (e.g. from their own dev store's webhook, which frequently has empty or fixed bodies).

### Likelihood Explanation
Exploitability depends on the attacker obtaining at least one legitimately-signed `(body, hmac)` pair, which is plausible for topics with static or highly predictable payload shapes (e.g., `{}` bodies, or bodies whose only real content the attacker also controls, such as many `app/uninstalled`- or `shop/redact`-style test payloads from their own store). No secret, token, or privileged access is required beyond that.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed content used for verification (or independently verify these header values against the session/shop registered for the delivery), so `to_signable_string` binds the full identity, not just the raw body.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and registers a webhook whose payload is empty/static (e.g. `customers/redact` often delivers `{}`).
2. Attacker captures the legitimate delivery: headers include `X-Shopify-Hmac-Sha256: <valid-hmac-for-{}>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: customers/redact`.
3. Attacker POSTs the same raw body `{}` and the same valid HMAC to the victim app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`).
4. `HmacValidator.validate(request)` in `Registry.process` [6](#0-5)  succeeds because it only checks `@raw_body`.
5. The app's handler receives `WebhookMetadata.new(topic: "customers/redact", shop: "victim-shop.myshopify.com", body: {}, ...)` and performs the corresponding action (e.g., data deletion) attributed to `victim-shop`, even though the signature never certified that shop or topic.

### Citations

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
