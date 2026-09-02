I found a valid analog. The webhook HMAC in this gem only covers the raw request body — not the `shop-domain` header that the gem later trusts as the tenant identity.### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then unconditionally trusts the `shop-domain` header (along with `topic`, `api_version`, `webhook_id`) as the tenant identity passed to the host app's handler — even though none of these headers are included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) . `Utils::HmacValidator.validate` computes the HMAC over `to_signable_string` and compares it to the `hmac-sha256` header [2](#0-1) . The `shop`, `topic`, `api_version`, and `webhook_id` values are all read directly from unauthenticated headers [3](#0-2) .

`Registry.process` validates the HMAC and then immediately builds the `WebhookMetadata` handed to the app's business logic using `request.shop` — a value that was never part of the signed payload: [4](#0-3) 

The binding the gem should enforce is:
`hmac_valid(raw_body) == true` implies `shop header == the tenant whose secret produced that HMAC`

But because the app's `api_secret_key` is a single value shared across *every* shop that installs the app (it is not a per-shop secret), a valid `(raw_body, hmac)` pair only proves "this body was signed with the app's secret" — it proves nothing about which shop the payload belongs to. The `shop-domain` header can be swapped to any other value while the HMAC remains valid, so the equality above does not hold: the gem accepts a valid signature yet reports an arbitrary, attacker-chosen `shop`.

### Impact Explanation
Any actor who can obtain one legitimate `(raw_body, hmac)` pair — e.g., an unprivileged merchant who has installed the app on their own store and thus legitimately receives real webhook calls with valid HMACs signed by the shared `api_secret_key` — can replay that exact body/HMAC to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header value. `Registry.process` will pass HMAC validation (since the body is untouched) and hand the host application a `WebhookMetadata` object asserting the payload belongs to a different, victim shop [5](#0-4) . Any host application that uses `data.shop` to route, store, or act on webhook data per-tenant (the documented purpose of this field) can be tricked into associating one shop's data/events with another shop's session/tenant record — a cross-tenant data-integrity violation attributable directly to this gem's webhook verification not binding the identity field it exposes as authoritative.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the app on any Shopify store (an ordinary, unprivileged action available to any Shopify merchant/developer), which yields real webhook deliveries with valid HMACs computed from the app's single shared secret, and (2) the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a modified `shop-domain` header, which is trivial since HTTP headers are entirely attacker-controlled and are not part of the signed material. No leaked credentials, TLS interception, or privileged access are needed — the gem's own webhook request/registry code is the sole point of trust for the `shop` field.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string (or otherwise cryptographically bind them, e.g. by verifying `shop` against a known/expected value or including it in the HMAC input) so a valid signature also attests to the identity fields the gem exposes to the handler. At minimum, `Webhooks::Request#to_signable_string` should not silently omit `shop-domain` while `Registry.process` treats `request.shop` as authoritative for tenant attribution.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, a legitimate but unprivileged action.
2. Shopify sends a real webhook to the app: body `B`, headers include `x-shopify-hmac-sha256: H` (computed by Shopify using the app's shared `api_secret_key` over `B`) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `B` and `H` (e.g., from their own endpoint logs, or by crafting a body whose HMAC they can derive via any oracle available to them as an app installer).
4. Attacker sends a forged HTTP request directly to the app's public webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [6](#0-5) .
6. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [5](#0-4) , causing the host application to process attacker-controlled data under the victim shop's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
