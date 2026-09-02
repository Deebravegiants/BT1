Found it: the webhook `shop` identity used by the app's handler comes from the `x-shopify-shop-domain` header, but the HMAC signature (`Utils::HmacValidator.validate`) only covers the raw request body — never the `shop-domain` header. This is the same bug class as the Linea `TokenBridge` finding: a security-relevant field (`sourceChainId`/`targetChainId` there, `shop` here) is consumed by downstream logic without being bound by the value that was actually integrity-checked (the chain-ID pair there, the HMAC there).

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `#shop` is read straight from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header [2](#0-1) . `Registry.process` validates the HMAC using only the body and then dispatches `request.shop` (the unverified header value) straight into the app's handler as the tenant identity [3](#0-2) .

### Finding Description
`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` header [4](#0-3) . For `Webhooks::Request`, `to_signable_string` is just the raw body bytes — none of the HTTP headers, including `shop-domain`, are part of the signed material [1](#0-0) . Consequently, an attacker who has ever legitimately captured (or replayed) one valid `(body, hmac)` pair for their own shop — e.g., their own installed instance of the app delivering the "shop/redact" or any subscribed webhook — can replay the exact same body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header naming a *different* merchant's shop. The signature check in `Registry.process` still passes, because the signature never depended on the shop header, and `WebhookMetadata` is built with the attacker-chosen `shop` value [5](#0-4) . This breaks the identity binding: `shop authenticated == shop the HMAC vouches for` is false; the value handed to the app's handler as "this webhook is from shop X" is actually just copied from an attacker-controlled header.

This is analogous to the Linea `TokenBridge.initialize` issue where `sourceChainId`/`targetChainId` were used to define protocol identity/routing without being covered by any consistency check — here, `shop` defines multi-tenant routing/identity without being covered by the only integrity check (`HmacValidator`) that the webhook pipeline performs.

### Impact Explanation
Any Rails/host app that trusts `WebhookMetadata#shop` (which this gem explicitly returns as the shop identity) to select which merchant's data/session/tenant record to update — the intended and documented use of the field — can be tricked into applying a webhook payload under a different, victim merchant's tenant identifier. Because HMAC validity itself is preserved, the host application has no signal that the shop attribution is forged. This is a cross-tenant integrity break driven entirely by this gem's `Request`/`Registry` design, satisfying the "cross-tenant access" criteria.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one genuine `(body, hmac)` pair signed with the app's secret for *some* shop (trivially available to any developer/merchant who installs the app themselves, since Shopify delivers real webhooks to every installer), and requires a webhook body that is valid/replayable independent of its declared shop (e.g., empty-body topics like `app/uninstalled`, or topics whose body doesn't itself reference the shop). This is a realistic scenario for any unprivileged party who has installed the app once.

### Recommendation
Include the `shop-domain` header (and ideally `webhook-id`/`api-version`) in the signed/verified material, or independently cross-check `request.shop` against the shop associated with the session/webhook-id looked up server-side, rather than trusting a raw header that sits outside the HMAC's coverage. At minimum, document/enforce that `WebhookMetadata#shop` must never be used as the sole tenant key without an additional binding (e.g., verifying the target webhook subscription's registered shop).

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; capture a real webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret), for a topic with body-independent handling (e.g., `app/uninstalled`, body `{}`).
2. Replay the request to the app's webhook endpoint with headers changed to:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-hmac-sha256: H` (unchanged)
   - `x-shopify-topic`, `x-shopify-webhook-id` as needed
   - body `B` (unchanged)
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks `B` against `H` [1](#0-0) .
4. `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` [5](#0-4) , causing the host app to act on the victim tenant using attacker-supplied, HMAC-unverified shop identity.

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
