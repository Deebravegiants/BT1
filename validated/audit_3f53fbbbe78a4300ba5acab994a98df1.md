### Title
Webhook `shop-domain` header is trusted for tenant routing without being bound to the HMAC-verified body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to app webhook handlers purely from an HTTP header, while the HMAC signature that `HmacValidator`/`Registry.process` checks is computed over the raw body only. The `shop` field is therefore "acted on but not covered by the HMAC," breaking the intended binding `shop that produced the signed bytes == shop the handler is told the event belongs to`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, independent of the body: [2](#0-1) 

`HmacValidator.validate` computes/compares the HMAC solely over `verifiable_query.to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` checks only that HMAC-over-body is valid, then immediately forwards the unauthenticated `request.shop` header value to the app's handler as the tenant identifier, with no cross-check that this shop is the one that actually produced/owns the signed body: [4](#0-3) 

Because the signature never covers `shop-domain`, `topic`, `webhook-id`, or `api-version`, any `(body, hmac)` pair that is valid for one shop is also valid when replayed with a different, attacker-chosen `shop-domain` header. An unprivileged attacker can obtain a legitimate `(body, hmac)` pair simply by installing the victim app on their own free/dev Shopify store (no privileged credentials, access tokens, or `client_secret` needed) and capturing one of its outgoing webhooks (e.g. `app/uninstalled`, `shop/redact`, or any webhook whose body is generic/shop-agnostic). The attacker then POSTs that identical body+HMAC to the app's public webhook endpoint but with the `shop-domain` header changed to the victim's `myshopify.com` domain. `Registry.process` will accept it as valid (HMAC matches) and hand the handler `shop: <victim-domain>`, causing the app to act on the victim tenant's data (e.g., delete/reset the victim's stored session, mark the victim as uninstalled, or perform other shop-scoped operations) — a cross-tenant integrity/access violation.

### Impact Explanation
This crosses a tenant boundary: an attacker with no access to the victim's credentials, access token, or the app's `client_secret` can cause the app to execute shop-scoped business logic (session deletion, data resets driven by "mandatory" GDPR/uninstall webhooks, etc.) against a shop they do not control, because the library's own signature check does not bind the `shop` value it exposes to handlers. This matches the "cross-tenant access" bucket of Critical impact under the given rules, since the gem's `Webhooks::Registry`/`Request` API is the trust boundary apps rely on when calling `Registry.process`.

### Likelihood Explanation
Likelihood is meaningfully constrained by the need for a body that is shop-agnostic (identical across installs) — many mandatory/system webhooks (e.g. `app/uninstalled`) have small, largely static JSON bodies, making a valid replay body easy to obtain. No privileged credential is required: any user can install a public app on their own store to harvest a valid signed payload. The main limiting factor is that the attacker must find/target a webhook topic whose body content does not itself encode the originating shop in a way the handler double-checks — which is exactly the gap this gem leaves for consuming apps, since it hands out `request.shop` as if it were authenticated.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) header into the value that is HMAC-verified, or otherwise document/enforce that `WebhookMetadata#shop` must not be treated as authenticated on its own. Concretely, `Request#to_signable_string` (or a new verification step in `Registry.process`) should incorporate the shop-domain header (and other Shopify-supplied headers used for routing) into the signed material actually validated, so that a signature valid for shop A's body cannot be replayed against shop B by merely swapping the header.

### Proof of Concept
1. Install the target app (which uses this gem's `ShopifyAPI::Webhooks::Registry`) on an attacker-controlled Shopify dev store.
2. Trigger an app-uninstall (or any other webhook with a small/static body) and capture the raw HTTP request Shopify sends to the app's webhook endpoint, including the `x-shopify-hmac-sha256` header and raw body.
3. Replay this exact captured request to the same webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `HmacValidator.validate` (checking only the body) succeeds; `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to run shop-scoped logic (e.g. wipe/reset stored session data) for a shop the attacker never installed on or authenticated against.

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
