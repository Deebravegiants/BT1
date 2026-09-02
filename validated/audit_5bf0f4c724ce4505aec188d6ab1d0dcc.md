### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`), `topic`, and `webhook_id` entirely from unauthenticated HTTP headers, while the HMAC signature that `ShopifyAPI::Utils::HmacValidator` verifies only covers the raw request body. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` to attribute the webhook to a tenant without any cryptographic binding between that value and the verified signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` reads the signature straight from the `hmac-sha256` header, and `#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it against the received signature: [3](#0-2) 

`shop`, `topic`, and `webhook_id` are read directly from headers, which are never part of the signed material: [4](#0-3) 

`Registry.process` validates only the HMAC and then hands `request.shop` straight to the handler as the tenant identifier, with no separate check that this shop value is consistent with anything cryptographically verified: [5](#0-4) 

Equality that should hold: `shop authenticated by HMAC == shop trusted by the handler for tenant routing`. In this implementation, the left side does not exist — the HMAC only authenticates that "some body byte-string was HMAC'd with this app's secret", never binding it to a particular shop. The right side (`request.shop`) is fully attacker-controlled input via HTTP headers. Since the raw body is unrelated to the shop header, any request with a body+HMAC pair that is valid for the app's secret (e.g., obtained from a legitimate webhook delivery to *any* shop that has installed the app — including one the attacker controls) can be replayed with an arbitrary `x-shopify-shop-domain` header, and it will pass `HmacValidator.validate` while being attributed to a different, victim shop.

### Impact Explanation
This breaks the shop/tenant identity boundary the gem is expected to enforce for webhook processing. An attacker who legitimately installs the target app on their own store receives real, validly-signed webhooks (body + HMAC) for their own shop. By replaying that valid body/HMAC pair while substituting the `x-shopify-shop-domain` (and/or `topic`/`webhook-id`) header, the attacker causes the host application's webhook handler to execute with `WebhookMetadata#shop` pointing at an arbitrary victim shop domain, while the body content is attacker-chosen. Any handler logic that uses `shop` to select which tenant's session/data to update (a standard, gem-endorsed pattern — see `docs/usage/webhooks.md`) can be manipulated into writing or acting on data associated with another merchant, a cross-tenant access/data-integrity violation.

### Likelihood Explanation
High for an attacker who is simply an unprivileged internet user relative to the target application: no `api_secret_key`, access token, or privileged account is required, only the ability to install the app on their own shop (which any Shopify store owner can do) and issue a replayed HTTP request with modified headers to the app's public webhook endpoint. The vulnerability is entirely within this gem's `Webhooks::Request`/`Registry.process`/`Utils::HmacValidator` code path, which is exactly the flow documented and recommended in `docs/usage/webhooks.md`.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-verified material, or otherwise cryptographically bind them to the signed request (e.g., require the shop domain used for tenant lookup to be independently verified — for example, cross-checked against a known/installed shop record — rather than trusted directly from the `x-shopify-shop-domain` header). At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and that host applications must independently verify it corresponds to a shop that legitimately has this webhook subscription/installation before using it for any tenant-scoped operation.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Shopify delivers a legitimate webhook (e.g., `orders/create`) to the app's webhook endpoint with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: <valid HMAC of raw body with app secret>`
   - body: `{"id": 123, ...}`
3. Attacker captures this request and replays it to the same endpoint, changing only the `x-shopify-shop-domain` header to `victim.myshopify.com` (topic/body left untouched, or changed since they are not covered by HMAC either).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-hashes the raw body — validation succeeds because the body/HMAC pair is unchanged.
5. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: ..., ...)`, causing the host app to process attacker-supplied data under the victim shop's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
