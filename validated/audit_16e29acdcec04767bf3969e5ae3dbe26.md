### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw request body, while the `shop-domain` header — which is the value the library hands to the app's handler as the tenant identifier — is never included in the signed material. This mirrors the reported bug class: a field that is *acted on* (the shop identity used downstream) is not covered by the authentication check (the HMAC) that gates the request.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively from `to_signable_string`, so it only ever authenticates the request body, never the `shop-domain` header: [2](#0-1) 

`Registry.process` gates entry solely on this body HMAC, then immediately trusts `request.shop` (parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header) as the tenant identity passed to the app's handler: [3](#0-2) [4](#0-3) 

The equality the code implicitly assumes but never enforces is:
`shop_bound_by_hmac == shop_delivered_to_handler`

Before the request: an attacker who already possesses one legitimately-signed (body, hmac) pair — for example from their own store where the same app is installed, or from any webhook delivery they can observe — controls a valid `(raw_body, hmac)` combination.
After the request: the attacker resends that same `(raw_body, hmac)` pair but substitutes an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` still succeeds (it never looks at the shop header), and `Registry.process` forwards the attacker-chosen `shop` value, unauthenticated, to the handler as `WebhookMetadata#shop`: [5](#0-4) 

This is the same class of defect as the reported issue: the identity used to route/act on a privileged operation (there: the pair address passed to `bulkWithdrawFees`; here: the `shop` tenant identity passed to the handler) is not bound by the same authentication mechanism (there: not checked against `splitterAddresses`; here: not included in the HMAC).

### Impact Explanation
Any app handler that uses `WebhookMetadata#shop` to key merchant-specific data (session lookup, database writes, tenant-scoped side effects) can be made to process a validly-HMAC'd payload under an attacker-chosen shop identity, i.e. cross-tenant confusion/spoofing of the shop context for an otherwise-authenticated webhook delivery.

### Likelihood Explanation
Exploitation requires the attacker to already possess at least one genuine `(body, hmac)` pair signed with the app's `api_secret_key` for *some* shop (e.g., their own store where the app is installed, which is a normal, unprivileged capability for any merchant who installs the app) — no leaked secret or privileged account is required. This is a realistic, unprivileged-user reachable path, matching Shopify's actual webhook signing behavior (HMAC over body only), which this library faithfully but insecurely surfaces to handlers as if `shop` were verified alongside the payload.

### Recommendation
1. Document explicitly (and enforce where feasible) that `WebhookMetadata#shop`/`request.shop` is **not** cryptographically bound to the HMAC and must not be trusted as an authenticated tenant identifier on its own.
2. Consider incorporating the `shop-domain` header into the signable material used for HMAC verification, or provide a separate verified-shop accessor that cross-checks the header against a value obtained through an authenticated channel (e.g., the registered webhook's expected shop, if known).
3. At minimum, add a prominent warning in `Registry.process`/`WebhookMetadata` and in the webhooks documentation that `shop` is unauthenticated header data and must be corroborated by the app before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`.
2. Attacker replays the identical `raw_body = B` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` parses `shop` as `"victim-shop.myshopify.com"`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only recomputes/verifies the HMAC over `B`: [6](#0-5) 
5. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and the handler acts on victim-shop data/state using attacker-supplied content `B`, believing the webhook was authenticated end-to-end.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
