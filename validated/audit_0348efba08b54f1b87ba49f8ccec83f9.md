## Title
Webhook shop-domain identity spoofing via HMAC that only covers the request body, not the `shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request **body**, then dispatches the handler using the **`shop-domain` header** as the tenant identifier. Because the header is never included in the signed data, the "shop" identity attached to a webhook event is not cryptographically bound to the HMAC that authenticates it.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

Specifically: [3](#0-2) 

`shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, with no relation to the signed body.

`Utils::HmacValidator.validate` verifies the received `hmac` against `verifiable_query.to_signable_string`, i.e. the raw body only: [4](#0-3) 

`Webhooks::Registry.process` treats a successful `HmacValidator.validate(request)` as proof the whole request is authentic, then forwards `request.shop` (the unauthenticated header) straight into the handler as the tenant identity: [5](#0-4) 

The binding the library implicitly claims is:
`hmac_valid(body, api_secret_key) == true` ⟺ `(body, shop) is an authentic event for shop`

But the actual equality enforced is only:
`hmac_valid(body, api_secret_key) == true` ⟺ `body is an authentic Shopify webhook body signed with this app's shared secret`

`shop` is completely outside that equality. Since `api_secret_key` is a single shared secret for the whole app (not per-shop), *any* merchant who installs the app can obtain a validly-signed `(body, hmac)` pair for their own store's events (e.g., by triggering an `orders/create` webhook on their own shop), then replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `Registry.process` will accept it as valid and hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion / cross-tenant access primitive (Critical): an unprivileged app installer can forge webhook events that appear to originate from a different (victim) merchant's shop, because the identity field the host application relies on (`shop`) is never covered by the cryptographic check that gates the whole request. Any host application that uses `data.shop` from `WebhookMetadata` (as the gem's own docs/tests direct developers to do) to select which tenant's records/session to mutate is exposed to cross-tenant writes/reads driven entirely by attacker-controlled request bodies and headers.

### Likelihood Explanation
Any user who can install the app on their own store (i.e., an ordinary, unprivileged merchant/attacker — no `api_secret_key`, no victim credentials, no privileged account needed) can capture a legitimately signed webhook delivery for their own shop and replay it with a modified `shop-domain` header to the same public webhook endpoint. No control over the app's secret or any victim credential is required.

### Recommendation
Bind the shop identity to the signed data:
- Include `shop-domain` (and ideally `topic`, `webhook-id`) in `to_signable_string`, or
- Independently authenticate `request.shop` by cross-checking it against a per-shop stored secret/session, or by verifying it via a separately signed/trusted channel, before handing it to handlers as the tenant identity.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`.
2. Attacker triggers any webhook topic on their own store, capturing the raw `body` and the resulting `X-Shopify-Hmac-Sha256` value Shopify computed with the app's shared secret.
3. Attacker POSTs to the app's webhook endpoint with the same `body`/`hmac`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, because the HMAC only covers `body`, unchanged from step 2: [6](#0-5) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, `body` fully attacker-controlled, and proceeds to act as if this were an authentic event from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
