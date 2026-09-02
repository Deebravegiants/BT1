## Title
Webhook shop attribution is not bound to the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `api_version`, `webhook_id`) that is handed to the app's webhook handler entirely from unauthenticated HTTP headers, while `ShopifyAPI::Utils::HmacValidator` (invoked from `ShopifyAPI::Webhooks::Registry.process`) only verifies the HMAC over the raw request body. Any party who can produce one HMAC-valid `(raw_body, hmac)` pair for the app's shared `api_secret_key` — e.g. an attacker who installs the app on their own shop and receives a genuine webhook — can replay that body with a different `x-shopify-shop-domain` header to make the host application process the payload as belonging to a victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` verifies the HMAC solely against that signable string: [2](#0-1) 

But `Registry.process` derives the tenant identity (`shop`), `topic`, `api_version`, and `webhook_id` from the request's headers — none of which are part of the HMAC-signed data — and passes them straight to the app's handler: [3](#0-2) 

```
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`Request#shop` simply reads the `shopify-shop-domain` / `x-shopify-shop-domain` header: [4](#0-3) 

The identity binding that should hold is:
`shop_bound_by_hmac == shop_delivered_to_handler`

In reality, the HMAC only binds `raw_body`, so:
`hmac.covers(raw_body) == true`, but `hmac.covers(shop_header) == false`

Because the same app `api_secret_key` is shared across every shop that installs the app (it is not per-shop), any unprivileged internet user can:
1. Install the app on their own (attacker-controlled) shop, and receive a genuine webhook delivery from Shopify — a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared secret.
2. Replay that exact body/HMAC pair directly to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`, also unauthenticated).
3. `HmacValidator.validate` passes because it only checks the (unchanged) body against the (unchanged) signature.
4. `Registry.process` reads `request.shop` from the forged header and calls the handler with `WebhookMetadata` claiming the event belongs to the victim shop.

Any host application that uses `data.shop` from `WebhookMetadata` to select tenant context — e.g. looking up the victim's stored session/access token to react to the (attacker-supplied) body, or handling `shop/redact`/`customers/redact`/`customers/data_request` compliance webhooks — will act on attacker-controlled data while attributing it to another tenant.

### Impact Explanation
This is a cross-tenant identity binding break: a field (`shop`, along with `topic`/`webhook_id`) that the gem exposes to and is acted upon by the host application is not covered by the cryptographic proof (HMAC) that the gem itself performs. It lets a shop-level attacker forge webhook events attributed to an arbitrary victim shop, satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any Shopify Partner or developer can install a public/custom app on a shop they control at no privilege beyond normal app installation, which is what the rules define as "unprivileged internet user." Once installed, they legitimately receive HMAC-signed webhook bodies for actions they themselves can trigger on their store (e.g. `orders/create`), giving them a valid `(body, hmac)` pair to replay with a forged shop header against the same app's public webhook endpoint.

### Recommendation
Bind the shop (and topic/webhook id) into the verified signature material, or otherwise cryptographically tie the header-derived shop to the signed body — e.g., include the relevant headers in the HMAC input, or require the host application to independently verify that the shop in the webhook maps to a session that was itself established through OAuth/HMAC-verified means before trusting `WebhookMetadata#shop` for tenant-sensitive actions. At minimum, document prominently that `shop`/`topic`/`webhook_id` are unauthenticated and must not be used as the sole tenant boundary.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a real event (e.g. creates an order) and captures the resulting webhook POST: raw JSON body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(app_secret, B)`).
3. Attacker POSTs the same body `B` and header `x-shopify-hmac-sha256: H` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and, if desired, a different `x-shopify-topic`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds since it only checks `B` against `H`: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, and any application logic keyed on `data.shop` operates as though the event genuinely originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
