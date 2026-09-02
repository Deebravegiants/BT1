### Title
Webhook `shop` (tenant identity) is trusted from an unauthenticated header while the HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value used to route/process a webhook from the `shopify-shop-domain` HTTP header, but the HMAC signature verified by `Utils::HmacValidator` covers only the raw request body. Because the tenant-identifying field (`shop`) is not part of the signed bytes, any party who can obtain one valid `(body, hmac)` pair for the app can replay it with a forged `shop-domain` header to make `ShopifyAPI::Webhooks::Registry.process` deliver attacker-chosen `shop`/`topic` metadata to the host application's webhook handler while still passing HMAC validation.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers without being covered by the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.shop` and `request.topic` (both unauthenticated header values) to build the `WebhookMetadata` object handed to the host application's handler: [3](#0-2) 

`Utils::HmacValidator.validate` simply recomputes the signature over `verifiable_query.to_signable_string` (the body) and compares it to the received HMAC — it has no knowledge of `shop` or `topic`: [4](#0-3) 

This breaks the identity binding: `handler-trusted shop == HMAC-authenticated shop` does not hold, since the HMAC authenticates only the body bytes, not the shop that will be reported to `WebhookMetadata#shop`. Anyone possessing one legitimate `(body, hmac)` pair for the app (e.g. a merchant who has the app installed and receives genuine webhooks for their own shop) can resend the same body/hmac to the app's webhook endpoint with a different `x-shopify-shop-domain`/`shopify-shop-domain` header value, and the library will report that forged shop identity to the handler as if it were authenticated.

### Impact Explanation
If the host application's webhook handler uses `WebhookMetadata#shop` to select which tenant's data/session to act on (a common and encouraged pattern, since `Registry.process` is the gem's documented API for handling webhooks), an attacker can cause webhook data intended to look like it originated from shop A to be processed and attributed to shop B — a cross-tenant confusion primitive built entirely from the gem's own trust boundaries (HMAC vs. header-derived shop).

### Likelihood Explanation
Exploitation requires the attacker to already have one legitimate `(raw_body, hmac)` pair signed with the app's `client_secret`. This is realistically obtainable by any merchant that installs the app (they legitimately receive real webhooks, including empty-body ones like `shop/redact` topic triggers or any topic with predictable/replayable bodies), so it does not require possessing the `api_secret_key` directly. The forging step (changing the shop header) requires no privileged access.

### Recommendation
Include the security-relevant identity fields (`shop`, `topic`) in the material that is cryptographically bound to the HMAC verification, or otherwise ensure the `shop` value delivered to handlers cannot be manipulated independently of the payload that was actually signed by Shopify — e.g. cross-check `request.shop` against a shop already known/stored for the given `webhook_id`/session before dispatching to a handler, and document to consumers that `WebhookMetadata#shop` is only as protected as the request headers, requiring the host framework to source headers strictly from the HTTPS connection to Shopify's servers (not client-controlled proxies).

### Proof of Concept
1. App has webhook endpoint wired to `ShopifyAPI::Webhooks::Registry.process(request)`.
2. Attacker (a merchant with the app installed on `attacker-shop.myshopify.com`) captures a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for `B` signed with the app's `client_secret`).
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `B`/`H`.
5. `Registry.process` builds `WebhookMetadata.new(topic: attacker-chosen, shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and invokes the host's handler, which believes the data originated from `victim-shop.myshopify.com`.

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
