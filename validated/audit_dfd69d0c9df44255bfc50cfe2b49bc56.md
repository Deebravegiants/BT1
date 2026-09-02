## Title
Webhook HMAC validation covers only the raw body, not the `shop-domain` header, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body alone, while the `shop` value used by the application/handler is read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header. This mirrors the ELF Protocol bug class of "a field acted on but not covered by the [security check]": the byte range that is HMAC-verified and the field that is trusted to identify the tenant are not the same.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shop-domain` header without any binding to the signed content: [2](#0-1) 

`Registry.process` validates the HMAC solely via `Utils::HmacValidator.validate(request)`, and then constructs `WebhookMetadata` directly from `request.shop`, `request.topic`, `request.parsed_body`, `request.webhook_id`, passing them straight to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate_signature` recomputes the signature over `verifiable_query.to_signable_string` (i.e., the raw body only) and compares it against the received `hmac`: [4](#0-3) 

Because the HMAC is computed with the app's shared `api_secret_key`, any *valid* webhook payload (one legitimately delivered to the app for any shop the app is installed on, including the attacker's own shop) has a correct HMAC that binds only the body bytes. Nothing prevents an attacker who controls the raw HTTP request from re-sending that same signed body with a forged `x-shopify-shop-domain` header naming a different (victim) shop. `Utils::HmacValidator.validate` will still return `true` because it never inspects the shop header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event originated from the victim shop.

This is the equality that should hold but doesn't:
`HMAC-verified bytes == bytes the handler trusts for tenant identity`
In this gem, `HMAC-verified bytes = raw_body` while `tenant identity = shop-domain header`, which is disjoint from the signed bytes.

### Impact Explanation
Any topic whose payload body doesn't itself encode the shop domain (e.g. many `app/uninstalled`, `shop/update`, `customers/redact`, GDPR, or generic ID-only payloads) is fully spoofable across tenants: an attacker with a legitimately installed instance of the app on their own shop can capture one authentic signed webhook body and replay it with an arbitrary victim `shop-domain` header. The host application (built on top of this gem's documented `Registry.process`/`Request` API) will treat the event as authoritative for the victim shop, since the gem asserts the webhook is "valid" based purely on the HMAC over the body. This can trigger cross-tenant side effects (e.g., marking a victim shop as uninstalled and deleting its session/data, or acting on the wrong tenant's stored session), which is a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires the attacker to be able to construct/send an arbitrary HTTP request to the app's webhook endpoint with attacker-chosen headers and a body they can obtain by having the app installed on any shop they control — no access token, `client_secret`, or privileged account is required. This is realistically reachable by any unprivileged internet user who can install the app on a shop they own to harvest one valid signed payload, then replay it against the app's public webhook endpoint with a different domain header.

### Recommendation
Include the `shop-domain` header (and ideally `topic`/`webhook-id`) as part of the value verified against the HMAC, or explicitly document/require that consuming applications independently verify `request.shop` corresponds to a shop with an existing, previously-established relationship (e.g. a stored session) before trusting it — rather than treating `Utils::HmacValidator.validate(request)` as validating the shop identity at all.

### Proof of Concept
1. Install the vulnerable app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook whose body doesn't include the shop domain (e.g. `app/uninstalled`) and capture the raw request: headers include a valid `x-shopify-hmac-sha256` computed over `raw_body` using the shared `api_secret_key`.
2. Replay the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `HmacValidator.validate` (per `lib/shopify_api/utils/hmac_validator.rb` lines 26-31) recomputes the signature over `raw_body` only and succeeds.
4. `Registry.process` (per `lib/shopify_api/webhooks/registry.rb` lines 188-200) invokes the handler with `WebhookMetadata` whose `shop` is `"victim.myshopify.com"`, even though the actual signed event came from the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
