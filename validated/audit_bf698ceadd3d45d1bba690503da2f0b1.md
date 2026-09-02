### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` only signs the raw HTTP body when computing the HMAC that `Registry.process` verifies, but the `shop` (merchant) identity used to route and attribute the webhook event to a tenant is read straight from an HTTP header that is never included in the signed content. Anyone able to produce (or replay) a body+HMAC pair valid for the app's `client_secret` can attach an arbitrary `shop-domain` header and have the event attributed to a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `Request#shop` is taken verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed payload: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which internally recomputes the HMAC only over `to_signable_string` (i.e., the raw body) and compares it to the `hmac` header value: [3](#0-2) [4](#0-3) 

After the HMAC check passes, `request.shop` (unauthenticated) is handed directly to the app's handler via `WebhookMetadata`, which the host application uses to determine which tenant/merchant record the event belongs to.

This breaks the intended identity binding: `shop authenticated by HMAC == shop the event is attributed to`. In reality, the HMAC only proves "signed with this app's `client_secret`" over the *body bytes*; it says nothing about which shop the header claims to be. Since a single app's `client_secret` is shared across every shop that installs the app, a valid `(raw_body, hmac)` pair obtained from — or replayable for — one shop's webhook delivery can be resubmitted to the app's public webhook endpoint with the `shop-domain` header swapped to any other shop that uses the app, and it will pass validation.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the app cannot trust that `request.shop` reflects the actual origin shop of a webhook, even though `HmacValidator.validate(request)` reports success. Depending on how the host application's webhook handlers use `WebhookMetadata#shop` (e.g., `app/uninstalled`, `customers/redact`, `shop/redact`, `orders/create`), an attacker could cause the app to process an event as if it came from a shop it did not originate from — leading to cross-tenant data corruption, spurious uninstall/redact processing against a victim tenant, or forged order/customer data being attributed to the wrong merchant. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires obtaining one valid `(raw_body, hmac)` pair signed with the app's `client_secret` — attainable by any shop that has installed the app and can trigger/observe its own webhook deliveries (e.g., via a store action that fires a webhook with attacker-controlled or predictable body content), or from a leaked/replayed webhook payload. No access to another shop's data, access tokens, or the app's `client_secret` itself is required, only reuse of a signature the attacker already legitimately possesses for their own tenant.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed content, or independently verify `request.shop` against a value derived from data that is itself covered by the signature (e.g., re-deriving/confirming the shop from the signed body payload where Shopify includes it, such as `myshopify_domain` in the webhook body) before trusting it for tenant attribution. At minimum, `Request#to_signable_string` should not allow the shop attribution used downstream to be sourced from data outside the signed bytes.

### Proof of Concept
1. App installs on `shop-a.myshopify.com` and receives (or triggers) a legitimate webhook, capturing the raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed as `HMAC-SHA256(client_secret, B)`).
2. Attacker (who controls `shop-a`, an installer of the app) sends a POST request directly to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only covers `B`), but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com` (a victim shop that also uses the app).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` which recomputes the HMAC over `request.to_signable_string` (`= B`) and succeeds, since `B` and `H` are unchanged.
4. The handler receives `WebhookMetadata.new(..., shop: "shop-b.myshopify.com", ...)` despite the event never having originated from `shop-b`, allowing forged/cross-tenant event processing.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
