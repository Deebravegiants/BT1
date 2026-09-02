## Title
Webhook Shop Identity Spoofing via HMAC That Only Signs the Body, Not the `shop-domain` Header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process` verify a webhook's authenticity by checking an HMAC of the **raw body only**. The tenant-identifying field — the `x-shopify-shop-domain` header consumed as `request.shop` — is never included in the signed payload, so it is not covered by the HMAC check at all. Any party that can obtain one valid `(body, hmac)` pair for the shared app secret (e.g. by triggering a real webhook delivery on their own installed shop) can replay that exact body/HMAC pair while forging the `shop-domain` header to any other shop that has the same app installed, and the registry will happily dispatch the (attacker-controlled) body to the app's handler labeled as belonging to the victim shop.

### Finding Description
`Utils::HmacValidator.validate` computes and compares an HMAC solely over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be just the raw HTTP body: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the signed body: [3](#0-2) 

`Registry.process` only calls `Utils::HmacValidator.validate(request)` (i.e. it validates `hmac(secret, body) == received_hmac`) and then dispatches the handler using the unauthenticated `request.shop`: [4](#0-3) 

The broken identity binding, stated as an equality that the code *should* enforce but doesn't:
`hmac(secret, body || shop || topic || webhook_id) == received_hmac`

What is actually enforced:
`hmac(secret, body) == received_hmac`, with `shop` (and `topic`/`webhook_id`) trusted verbatim from headers.

Because the app's `client_secret` (the webhook signing secret) is shared across every shop that installs the app, any shop owner who has legitimately installed the app can trigger a real webhook delivery to obtain a valid `(body, hmac)` pair for content they control (e.g. via an `orders/create`, `app/uninstalled`, `customers/redact`, or `shop/redact` event on their own store, or by using a temporary tunnel to see raw deliveries). They can then replay that exact `body` + `hmac-sha256` pair directly against the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. The signature still validates (it never depended on the shop), and `Registry.process` forwards the payload to the app's handler tagged as coming from the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to guarantee: the app has no cryptographic assurance that the webhook body it is processing actually originated from, or pertains to, the shop named in the `shop-domain` header. Depending on how the host app's webhook handler uses `WebhookMetadata#shop` (e.g. mandatory `shop/redact` / `customers/redact` compliance handlers, order/inventory sync, session invalidation on `app/uninstalled`), an attacker who merely has their own shop install of the app can cause the victim shop's records to be modified, deleted, or polluted with attacker-chosen data — a cross-tenant data integrity/confidentiality violation without ever touching the victim's credentials or the app's `client_secret`.

### Likelihood Explanation
The only prerequisite is installing the target app on any shop the attacker controls (a normal, unprivileged action available to any merchant) and being able to reach the app's public webhook endpoint. No leaked secrets, TLS interception, or privileged access is required — the gem's own HMAC verification logic (`hmac_validator.rb` + `webhooks/request.rb`) is the root cause, not host-application misuse.

### Recommendation
Include the tenant-identifying and message-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material used by `to_signable_string`, or otherwise cryptographically bind `request.shop` to the verified body (e.g. verify shop against a known/registered shop list tied to the session that originally requested the webhook, in addition to signing headers). At minimum, document that `Registry.process`'s HMAC check does not authenticate the `shop-domain` header and host apps must not trust it for tenant scoping without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` (a normal unprivileged action).
2. Attacker triggers a webhook event on their own shop (e.g. updates an order) and captures the resulting `raw_body` and `X-Shopify-Hmac-Sha256` value delivered to the app's endpoint (e.g. via a temporary reverse proxy/logging endpoint they control during development).
3. Attacker sends a new POST request directly to the production app's webhook endpoint with:
   - the exact same `raw_body`
   - the exact same `X-Shopify-Hmac-Sha256` header (still valid, since HMAC only depends on `secret` + `body`)
   - `X-Shopify-Topic` and `X-Shopify-Shop-Domain` headers rewritten to a victim shop, e.g. `victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `hmac(secret, raw_body)`.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed_body>, ...)`, causing the app to act on attacker-supplied data under the victim's identity. [4](#0-3) [2](#0-1)

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
