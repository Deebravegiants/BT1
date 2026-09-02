[1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook Shop Identity Not Bound to HMAC, Enabling Cross-Tenant Header Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content solely from the raw request body, never including the `shop-domain` header. `Registry.process` trusts `HmacValidator.validate` as proof of authenticity for the entire request, then hands the unauthenticated `shop` value straight to the app's webhook handler. This mirrors the reported `hbridge` bug class: an authentication check occurs, but the field the code subsequently acts on (the shop/tenant identity) is never covered by that authentication, so the two "authenticated" identities can be split apart.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [4](#0-3) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic tie to the body or the HMAC: [5](#0-4) 

`HmacValidator.validate` proves only that `to_signable_string` (i.e., the raw body) matches the HMAC computed with `Context.api_secret_key`; it never inspects or incorporates the `shop` header into the signature check: [3](#0-2) 

`Registry.process` treats a passing `HmacValidator.validate(request)` as authorization for the *entire* request, then forwards `request.shop` (the unauthenticated header) to the handler as the tenant identity: [2](#0-1) 

The security model this creates is:
- **Authenticated**: `raw_body` is genuinely from Shopify (HMAC-verified with the shared `api_secret_key`).
- **Trusted but unauthenticated**: `shop` header, which is used by the handler (via `WebhookMetadata#shop`) to key persistence/business logic to a tenant.

Because the same `api_secret_key` is shared across every shop installed on a given app, any legitimately-received webhook body/HMAC pair (e.g. one delivered to a merchant's own installation, or observed via any means that gives access to the raw POST) remains HMAC-valid when replayed to the app's webhook endpoint with the `shop-domain` header rewritten to a different (victim) shop. The library performs no secondary check that the header-declared shop matches anything inside the authenticated body, so `Registry.process` will happily dispatch the handler with attacker-chosen `shop` while `body`/`topic` stay verified. This is the same class of flaw as the report: `authenticate()`-style verification (`ft4.auth.verify_signers`/`HmacValidator.validate`) succeeds, but the value used afterwards to bind the operation to an account/tenant (`address`/`shop`) was never part of what was cryptographically checked.

### Impact Explanation
This breaks the equality `shop_authenticated == shop_used_for_tenant_dispatch`, letting a party who can obtain (not forge) one valid webhook body/HMAC pair for the app attribute that payload to an arbitrary other shop identifier when replaying it to the app's shared webhook endpoint. Any host application that relies on `WebhookMetadata#shop` from this gem to select which tenant's data/session to mutate (a documented, intended usage per `docs/usage/webhooks.md`) inherits cross-tenant data confusion, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation needs only: (1) the ability to send arbitrary HTTP requests to the app's public webhook endpoint (any unprivileged internet user, since this endpoint is unauthenticated by design other than the HMAC), and (2) possession of one valid raw-body/HMAC pair, which is obtainable without secrets by any shop that has installed the app and can observe/capture its own inbound webhook traffic. No `api_secret_key`, access token, or privileged credential is required to perform the header-rewrite/replay itself.

### Recommendation
Bind the shop identity into the value that is HMAC-verified, e.g. include the `shop-domain` header (and ideally `webhook-id`, to prevent replay) in `Request#to_signable_string`, or otherwise cryptographically tie the declared shop to the authenticated body before `Registry.process` passes it to handlers.

### Proof of Concept
1. Shop A installs the app and captures a legitimate webhook delivery: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's shared secret), and header `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker (Shop A's operator, or anyone who obtained `B`/`H`) POSTs the same body `B` and same `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `Registry.process` calls `HmacValidator.validate(request)`, which passes because it only checks `B` against `H` per `lib/shopify_api/utils/hmac_validator.rb` lines 12-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38.
4. The handler receives `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: parsed(B), ...)` per `lib/shopify_api/webhooks/registry.rb` lines 198-199, causing the app to process Shop A's webhook content under Shop B's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
