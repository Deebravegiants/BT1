### Title
Webhook shop/topic identity spoofing — HMAC only covers the raw body, not the shop-domain header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields consumed by `ShopifyAPI::Webhooks::Registry.process` are read straight from unauthenticated HTTP headers and are never included in the HMAC computation. Any party who can produce one valid `(raw_body, hmac)` pair — trivially available to any merchant who has the app installed, since the webhook signing secret is the app's single shared `client_secret`, identical for every shop — can replay that pair to the app's public webhook endpoint while freely substituting the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`) headers. `HmacValidator.validate` will report the forged request as valid, and the handler will process attacker-supplied data under an arbitrary, attacker-chosen shop identity.

### Finding Description
The webhook signature binding is defined here: [1](#0-0) 

`hmac` is derived from the `X-Shopify-Hmac-Sha256` header, and `to_signable_string` returns `@raw_body` exclusively. `topic`, `shop`, `webhook_id`, and `api_version` are all pulled from other, HMAC-uncovered headers via `shopify_header`: [2](#0-1) 

`Registry.process` validates only the byte-string that `to_signable_string` returns, then immediately trusts `request.topic` and `request.shop` to route and label the event: [3](#0-2) 

`HmacValidator.validate` performs `HMAC-SHA256(secret, verifiable_query.to_signable_string) == received_hmac`: [4](#0-3) 

Because `to_signable_string` == `raw_body` only, the equality the code actually enforces is:

`HMAC(secret, raw_body) == received_hmac`

but the identity binding the application relies on for tenant isolation is:

`shop_header == shop_that_the_signature_was_issued_for`

These are not the same equality — the shop header is never an input to the HMAC. Since the app's webhook signing secret (`client_secret`) is shared across every shop that has the app installed (it is not per-shop), any merchant who legitimately installs the app can capture one authentic `(raw_body, X-Shopify-Hmac-Sha256)` pair from a webhook Shopify sends to their own store. That pair remains valid for **any** value of `X-Shopify-Shop-Domain`, because the header is not part of the signed content. The attacker can then POST the same raw body and HMAC to the app's public webhook endpoint with the header rewritten to a victim shop's domain (and/or a different topic), and `Registry.process` will accept it as an authentic event for the victim shop.

### Impact Explanation
This breaks the tenant boundary the webhook signature is supposed to enforce (`Impact: Critical — cross-tenant access`). An attacker with no privileges beyond having the app installed on any shop (including a free/dev store they control) can:
- Inject fabricated webhook events attributed to a victim merchant's shop (e.g., `orders/create`, `app/uninstalled`, `customers/redact`, etc., depending on which topics the app registers), causing the host application's webhook handlers to create, modify, or delete data keyed by the victim's `shop` using attacker-chosen body content.
- Because `shop` is the tenant key most host applications (e.g., the `shopify_app` reference implementation) use to look up sessions/records, this is a direct cross-tenant data-integrity/isolation break, not merely a spoofed log entry.

### Likelihood Explanation
Reaching this requires only:
1. Installing the target app on any shop (a normal, unprivileged action any internet user with a Shopify Partner/dev account can perform for public apps), to obtain one legitimate `(raw_body, hmac)` pair.
2. Sending an HTTP POST to the app's publicly reachable webhook endpoint with headers of the attacker's choosing.

No access token, no leaked `client_secret`, and no privileged account are required — only the ability to receive one webhook for a shop the attacker already controls, which is part of ordinary app usage. This is squarely within the unprivileged-internet-user threat model and does not depend on the host application ignoring documented gem behavior; `Registry.process`/`Webhooks::Request` are the gem's own documented webhook verification API.

### Recommendation
Bind the tenant-identifying fields into the signed content, or otherwise cryptographically tie `shop`/`topic` to the verified signature, e.g.:
- Change `to_signable_string` to include a canonical representation of `shop`, `topic`, and `webhook_id` alongside `raw_body`, and require Shopify to include these in the signed payload (matching what Shopify's webhook signature actually spans), or
- After HMAC validation, cross-check the asserted `shop` against a value obtained through a channel that is bound to the signature (for example, validating that the shop is one for which a session/install record already exists **and** rejecting duplicate/replayed `webhook_id`s), so a captured signature for shop A cannot be replayed to attribute events to shop B.
At minimum, document and enforce that host applications cannot trust `WebhookMetadata#shop` without additional verification, since the current design allows the header to be forged independent of the signature.

### Proof of Concept
```ruby
# Attacker legitimately receives one real webhook for their own shop "attacker.myshopify.com":
raw_body = '{"id":1}'
hmac_b64 = "<value captured from a real X-Shopify-Hmac-Sha256 header sent by Shopify for the attacker's own shop>"

# This hmac_b64 is HMAC-SHA256(app_client_secret, raw_body) -- shop is not part of the input.
# It is therefore valid for ANY shop-domain header, since the app's client_secret
# is the same for every installed shop.

forged_headers = {
  "x-shopify-topic"       => "orders/create",           # attacker-chosen, not signed
  "x-shopify-hmac-sha256" => hmac_b64,                    # captured from attacker's own real webhook
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged: not part of the HMAC input
  "x-shopify-webhook-id"  => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# Passes: HmacValidator.validate only checks HMAC(secret, raw_body) == hmac_b64
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "orders/create",
#                                              shop: "victim-shop.myshopify.com",  # spoofed tenant
#                                              body: JSON.parse(raw_body), ...))
```
`Registry.process` at [5](#0-4)  will not raise `Errors::InvalidWebhookError`, because `HmacValidator.validate` at [6](#0-5)  only re-derives the HMAC from `raw_body` (via `to_signable_string`), never from the `shop` header.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
