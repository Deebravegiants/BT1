### Title
Webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) headers are not covered by the HMAC signature, breaking the shop-identity binding used by webhook handlers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` verifies solely the integrity of `@raw_body`. The `shop` attribute (read from the `x-shopify-shop-domain` / `shopify-shop-domain` header) is never part of the signed material, yet it is the value trusted by `Registry.process` to identify which tenant the webhook belongs to and is forwarded verbatim to the app's handler.

### Finding Description
The binding that should hold is:

```
HMAC-verified(bytes) == bytes the app acts on for tenant identification
```

Concretely: `shop` used to route/act on a webhook == `shop` cryptographically bound inside the HMAC-verified payload.

In this gem that equality does not hold:

- `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 
- `shop` is parsed straight from an HTTP header, entirely outside the signed bytes: [2](#0-1) 
- `Registry.process` validates the HMAC over `to_signable_string` (i.e. the body) and, once that check passes, blindly trusts `request.shop` (together with `request.topic`, `request.api_version`, `request.webhook_id`, all header-derived) and hands them to the registered handler: [3](#0-2) 
- `HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, so it never touches the shop header: [4](#0-3) 

Because the HMAC is computed exclusively from the JSON body, an attacker who can capture (or is legitimately sent, e.g. from their own installed test shop) one genuine Shopify webhook — valid body + valid `hmac-sha256` header — can freely rewrite the `x-shopify-shop-domain` header to any other tenant string before re-delivering the request to the app's webhook endpoint. `Utils::HmacValidator.validate(request)` still succeeds because it only re-hashes `@raw_body`, which is untouched. `Registry.process` then constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-controlled shop value and invokes the app's handler as if the event legitimately originated from that shop.

This is directly analogous to the referenced report's bug class: a field that is acted upon (`shop`, used as the tenant/session key for the webhook) is not covered by the authentication primitive (HMAC) that is supposed to bind the whole message together — exactly the "shop authenticated versus shop used as session key" mismatch called out in scope.

### Impact Explanation
Any app whose webhook handler uses `WebhookMetadata#shop` to look up, create, or mutate per-tenant records (the documented and expected usage pattern shown in `docs/usage/webhooks.md`) can be made to act on the wrong tenant's data using a body that passed HMAC verification for a different tenant. This is a cross-tenant confusion vector rooted in this gem's webhook verification design: `Registry.process`/`Request` present the shop as verified when it is not. Depending on the payload shape (webhooks whose body doesn't embed the shop, e.g. `app/uninstalled` with minimal body, or bodies identical across shops), this can let an unprivileged actor with access to any one legitimate webhook delivery cause the app to process/act as if the event came from an arbitrary other shop — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only capturing or generating one legitimate, HMAC-valid webhook delivery (e.g. via the attacker's own shop installing the app, or via traffic interception of any delivered webhook) and replaying it toward the app's public webhook endpoint with a modified `shop-domain` header — no `api_secret_key`, access token, or privileged credential is needed, and no reliance on the host app "misusing" this gem's API: this is the intended, documented usage path (`ShopifyAPI::Webhooks::Registry.process`).

### Recommendation
Include the identity/routing headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind them to the body (e.g., concatenate normalized header values with the raw body before computing/verifying the digest), so that `Utils::HmacValidator.validate` fails if any of these header values are tampered with independently of the body.

### Proof of Concept
1. App receives (or attacker triggers via their own shop) a legitimate webhook to the app's endpoint:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`, `x-shopify-topic: app/uninstalled`
   - Body: `{}` (or any body that carries no shop-specific data)
2. Attacker replays the exact same body and `x-shopify-hmac-sha256` value, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`, and sends it to the app's webhook endpoint.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` from the tampered header: [2](#0-1) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only re-hashes `@raw_body` — unchanged — so validation passes: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"`, even though that value was never verified: [6](#0-5)

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
