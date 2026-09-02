### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw request body, but the `shop` (and `topic`/`webhook_id`/`api_version`) values that identify *which tenant* the webhook belongs to are read from unsigned HTTP headers. This breaks the binding `shop authenticated by HMAC == shop delivered to the handler as the tenant identity`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements the `VerifiableQuery` interface used by `Utils::HmacValidator`. Its `to_signable_string` method returns only the raw body bytes: [1](#0-0) 

Meanwhile `shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight out of request headers, which are never part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` only ever hashes `verifiable_query.to_signable_string` (i.e. the body) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` uses this same HMAC check to decide the request is legitimate, and then forwards the *header-derived, unauthenticated* `shop` value straight into `WebhookMetadata`, which is what the host application's handler receives as the tenant identity for the webhook payload: [4](#0-3) 

Because `Context.api_secret_key` is the app's single `client_secret`, shared across every shop that installs the app (not a per-shop key), any shop that legitimately receives one webhook (body + valid HMAC) obtains a body/HMAC pair that stays valid regardless of which `shop`/`x-shopify-shop-domain` header accompanies it. Swapping the `shop` header on a replayed, HMAC-valid body does not invalidate the signature check, since the header is outside the signed bytes.

Binding broken (as an equality):
`shop_verified_by_hmac (∅, not signed) != shop_used_as_tenant_identity (header value delivered to handler)`

### Impact Explanation
This is a cross-tenant confusion vector: a party who can obtain any one legitimate webhook body+HMAC pair for the app (e.g. by installing the app themselves and capturing their own real webhook, since HMAC only proves knowledge of the shared `client_secret`, not shop identity) can replay that exact body with an attacker-chosen `x-shopify-shop-domain` header claiming to be a different, victim shop. `Registry.process` will accept it (HMAC over body passes) and hand the host application a `WebhookMetadata` asserting the body came from the victim shop. If the host application's webhook handlers key their side effects (data writes, deletions such as `customers/redact`/`shop/redact`, cache updates, order processing) off `WebhookMetadata#shop` — which is exactly the intended and documented use of that field — this enables cross-tenant data injection/corruption without any credential of the victim shop.

### Likelihood Explanation
Exploitation requires only: (1) being (or having briefly been) an installer of the same app to legitimately receive one real webhook with a valid HMAC, and (2) the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a forged `shop-domain` header while reusing the captured raw body — no `access_token`, no `client_secret`, and no privileged account needed. This satisfies the unprivileged-internet-user threat model.

### Recommendation
Bind the tenant identity to the authenticated bytes: include `shop` (and ideally `topic`/`webhook_id`) in the value hashed for HMAC verification, or otherwise cryptographically tie the header-derived `shop` to the signed body before it is handed to `WebhookMetadata`/the handler, so that a valid HMAC can only be produced for the specific `shop` it accompanies.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: raw body `B` with headers `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the shared `client_secret`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker sends a forged HTTP request to the same app webhook endpoint with the identical body `B` and identical `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `to_signable_string` is still `B` (lib/shopify_api/webhooks/request.rb:36-38), so `Utils::HmacValidator.validate` succeeds (lib/shopify_api/utils/hmac_validator.rb:13-22) — the HMAC never covered the `shop` header.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` (lib/shopify_api/webhooks/registry.rb:198-199), even though the body/topic never originated for `victim.myshopify.com`. Any handler logic keyed on `data.shop` now operates against the wrong tenant.

### Citations

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
