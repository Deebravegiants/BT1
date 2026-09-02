The webhook processing logic in this gem is the strongest analog for this class of bug: the HMAC signature covers only the raw request body, while the tenant-identifying `shop-domain` header (and `topic`/`webhook-id` headers) are trusted without being cryptographically bound to that signature.

### Title
Webhook `shop` (and `topic`/`webhook-id`) headers are trusted for tenant identity without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then dispatches the parsed body to the app's handler tagged with the `shop` value taken straight from the `X-Shopify-Shop-Domain` header. That header is never included in the signed material, so the binding "HMAC-verified request == request whose `shop` field is trusted" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers without any cryptographic binding to that body: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the HMAC over exactly that `to_signable_string` value and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust `request.shop` as the tenant identity and forwards it to the app's webhook handler: [4](#0-3) 

The equality the code implicitly assumes is:
`HMAC-valid(raw_body)` ⇒ `shop header == shop that generated raw_body`

but since `shop-domain` is never part of the signed bytes, this equality does not hold. Any request whose body+HMAC pair is valid for shop A also passes validation with an arbitrary `X-Shopify-Shop-Domain` header claiming shop B, because the signature check is blind to that header.

### Impact Explanation
A Shopify merchant (unprivileged, does not need `api_secret_key`, access tokens, or any special privilege — merely to install the target app on their own store to receive genuine webhooks addressed to them) can capture one legitimately-signed webhook (body + `X-Shopify-Hmac-Sha256`) delivered to their own shop, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different shop's domain in `X-Shopify-Shop-Domain`. `Registry.process` will pass HMAC validation (it only checks the body) and hand the application's webhook handler a `WebhookMetadata` object claiming the payload belongs to the victim shop: [5](#0-4)  If the consuming application uses `data.shop` to select which tenant's records to update/create (a documented, expected usage pattern per this gem's `WebhookMetadata` API), the attacker can inject or corrupt data attributed to a shop they do not own — a cross-tenant integrity violation.

### Likelihood Explanation
Likelihood is moderate to high in practice: exploitation requires no secret material, only a normal app installation on any store to obtain one authentic signed webhook, and a trivial HTTP replay with one header changed. This is fully within the reach of an "unprivileged internet user" as defined by the rules, since it only depends on the gem's own `Request`/`Registry`/`HmacValidator` implementation, not on host-application misbehavior beyond the documented, expected use of `WebhookMetadata#shop`.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) values into the material that is verified, or otherwise cryptographically tie them to the signed body — e.g., have `HmacValidator`/`Request#to_signable_string` incorporate the shop-domain header (or require callers to independently confirm `request.shop` corresponds to a known, previously-established session/tenant) before trusting it for tenant-scoped side effects. At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is *not* authenticated by the HMAC check and must not be used as the sole tenant identifier for privileged operations.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) to be delivered to the app's webhook endpoint. They capture the raw POST body `B` and the `X-Shopify-Hmac-Sha256: H` header — both valid, since Shopify itself computed `H = HMAC-SHA256(client_secret, B)`.
2. Attacker resends the identical request to the same endpoint, but changes `X-Shopify-Shop-Domain` from `attacker.myshopify.com` to `victim.myshopify.com`, keeping body `B` and header `H` unchanged.
3. In `ShopifyAPI::Webhooks::Registry.process`, `Utils::HmacValidator.validate(request)` recomputes HMAC over `request.to_signable_string` (`== B`) and compares to `H` — this still matches, since neither depends on the shop header: [6](#0-5) 
4. The handler is invoked with `shop: "victim.myshopify.com"` and the attacker-supplied body, even though the victim shop never sent this webhook: [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
