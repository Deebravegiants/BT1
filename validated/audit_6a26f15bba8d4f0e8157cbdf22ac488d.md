### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then trusts the `shop` value taken from an unauthenticated HTTP header to route/attribute the webhook to a specific merchant. This breaks the intended binding `hmac == HMAC(secret, signed_fields)` where `signed_fields` should equal all data the handler treats as trusted (`shop`, `topic`, `body`), but in fact `signed_fields == raw_body` only.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 
`shop` is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header, with no cryptographic tie to the HMAC.

`to_signable_string`, which is what `HmacValidator` actually verifies, returns only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately forwards the unauthenticated `request.shop` to the handler as the tenant identity for the webhook: [3](#0-2) 

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string` (i.e., the body) and compares it against the `hmac` field, never incorporating `shop` or `topic`: [4](#0-3) 

Because the signature only binds the JSON body, any request whose body was legitimately signed by Shopify for one shop can be replayed with a different `shopify-shop-domain` header value and will still pass HMAC validation — the `handler.handle` call receives `WebhookMetadata` with an attacker-chosen `shop`, even though the cryptographic guarantee only ever covered the body bytes: [5](#0-4) 

This is exactly the "field acted on but not covered by the HMAC" identity-binding class described in the report: `y` (here, the `shop` field consumed by the handler) is never checked against what was actually authenticated (the body only).

### Impact Explanation
A host application that (as this gem's own `WebhookMetadata` API encourages, via `webhook_id:`, `shop:`, `topic:`) uses `data.shop` to decide which merchant record to update, delete, or notify would perform cross-tenant writes/reads if fed a replayed body with a forged `shop-domain` header. This matches the "Critical – cross-tenant access" impact bucket, since the identity boundary between merchants/tenants is enforced entirely by an HMAC that does not cover the value used to select the tenant.

### Likelihood Explanation
Exploitation requires the attacker to already possess at least one validly-HMAC-signed webhook body (e.g., from their own installed shop, or a body they can otherwise obtain/observe, such as through a shared/public webhook payload format for a topic they control). They do not need the app's `client_secret` or an access token — they only need to replay body bytes they legitimately received with a modified `shop-domain` header value, which is fully within an unprivileged internet user's capability once they control any shop that has the app installed. This is a realistic, low-effort attack path.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed/verified material, or independently verify that the `shop-domain` header corresponds to a shop known to have produced this exact signed body (e.g., look up the shop's own secret if per-shop secrets exist, or fail if `shop` is not cross-checked against session/install records before dispatching to the handler). At minimum, document loudly that `data.shop` in `WebhookMetadata` is NOT cryptographically authenticated by `HmacValidator.validate`, and require host applications to verify `shop` against their own installed-shop registry before trusting it as a tenant identifier.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook: body `B`, headers include `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same body `B` and HMAC header `H` to the app's webhook endpoint, but changes the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` builds the object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` → returns body `B` only, computes HMAC over `B`, matches `H` → validation succeeds: [6](#0-5) 
4. `handler.handle` is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed(B) ...)`, and the host application processes/attributes data `B` to `victim-shop.myshopify.com` even though it was never actually sent by or for that shop.

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
