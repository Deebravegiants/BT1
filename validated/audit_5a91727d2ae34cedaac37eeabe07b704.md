### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats `Utils::HmacValidator.validate(request)` as proof that a webhook is authentic and forwards `request.shop` straight to the app's handler as the tenant identity. However, the HMAC only signs the raw request body; the `shop` field is read from an unauthenticated header and is never bound to the signature. Anyone holding one valid `(body, hmac)` pair — e.g., an unprivileged user who installs the app on their own shop and receives a genuine, signed webhook — can replay that exact body and signature while substituting an arbitrary `x-shopify-shop-domain` value, and the library will accept it as an authentic webhook for the victim shop.

### Finding Description
`HmacValidator.validate` calls `validate_signature`, which computes the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body — the `shop` (and `topic`, `webhook_id`, `api_version`) fields come from separate headers that are excluded from the signed material: [2](#0-1) 

`Registry.process` uses this HMAC check purely as a gate, then trusts `request.shop` unconditionally when constructing the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

The equality that should hold is:
`shop bound by HMAC == shop delivered to the handler`

but the actual behavior is:
`shop delivered to the handler == shop header value (unauthenticated)`

Because the signature never covers `shop`, `topic`, `webhook_id`, or `api_version`, any party who can obtain one legitimately-signed `(raw_body, hmac)` pair (trivial for an unprivileged user — just install the app on a shop they control and capture Shopify's real webhook delivery) can resend that exact body/HMAC combination with a different `x-shopify-shop-domain` header pointing at a victim shop. `HmacValidator.validate` still succeeds because it only re-derives the HMAC from the (unmodified) body, and `Registry.process` calls the app's handler with `shop: <attacker-chosen victim domain>`. Downstream apps that key their per-tenant data (sessions, orders, customer records, webhook de-dup logic, etc.) off `data.shop` — the documented and expected usage pattern — will process attacker-supplied webhook content under the identity of a shop the attacker does not own.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: an attacker who is a legitimate (if malicious) installer of the app on their own store can forge webhooks that the host application will attribute to a shop it doesn't control, since `shop` is not part of the signed payload. This is a cross-tenant identity-binding bypass consistent with the "Critical - cross-tenant access" impact category: it lets one tenant's authenticated webhook traffic be relabeled as another tenant's, feeding attacker-controlled body content into per-shop application logic under a spoofed shop identity.

### Likelihood Explanation
Exploitation only requires the capability an ordinary, unprivileged app-installing user already has: install the target app on any shop and observe one real webhook delivery (body + HMAC). No `api_secret_key`, access token, or privileged access is required to mount the replay — the attacker only replays what Shopify already sent them, with a modified header. The gem provides no mechanism to bind `shop` to the signature, so every deployment using `Registry.process`/`Webhooks::Request` as documented is affected.

### Recommendation
Include the shop domain (and ideally topic/webhook_id) in the HMAC-verified signable material, or otherwise cryptographically bind the shop identity conveyed to the handler to the signed body (e.g., require the app to independently confirm that the given `shop` has an active session/webhook registration matching `webhook_id` before trusting it). At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated and must not be trusted for tenant-scoping decisions unless cross-checked against the app's own webhook subscription records.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a real webhook: body `{"secret":"data"}` with a valid `x-shopify-hmac-sha256` computed over that body using the app's `api_secret_key`.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`:
```ruby
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_valid_hmac, # from step 1, unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, not covered by HMAC
}
request = ShopifyAPI::Webhooks::Request.new(raw_body: '{"secret":"data"}', headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds because it only checks the body bytes.
# The handler is invoked with data.shop == "victim-shop.myshopify.com".
```
3. The host application's handler processes this payload under the victim shop's identity, even though the victim never sent it.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
