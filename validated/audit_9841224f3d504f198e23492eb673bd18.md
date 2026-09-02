## Title
Webhook `shop-domain` (and `topic`/`webhook-id`) not bound to HMAC signature — cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
This mirrors the CCTP `authorize` flaw where one field (`mint_recipient`) is validated but a sibling field (`destination_domain`) that determines the actual recipient of funds is not. In this gem's webhook path, `ShopifyAPI::Utils::HmacValidator.validate` cryptographically verifies only the raw request body, while the `shop-domain`, `topic`, and `webhook-id` headers — which determine which tenant/handler the event is attributed to — are never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns just `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes and compares the HMAC purely over that signable string: [2](#0-1) 

`Registry.process` trusts `request.shop` (taken straight from the `shop-domain`/`x-shopify-shop-domain` header) to build the `WebhookMetadata` handed to the app's handler, after only checking `HmacValidator.validate(request)`: [3](#0-2) 

`request.shop` is read directly from the header with no cross-check against the signed body: [4](#0-3) 

The identity binding that should hold is:
`shop_attributed_to_event == shop_actually_covered_by_hmac`

but because `shop-domain` is never part of `to_signable_string`, the equality can be broken: the HMAC only proves "this body was signed by the app's `api_secret_key`," not "this body belongs to shop X."

### Impact Explanation
The `api_secret_key` (the HMAC key) is shared across every merchant install of the app, not scoped per shop. An unprivileged user who installs the app on their own store receives legitimately signed webhook deliveries (valid `body` + valid `hmac`) for that store. Because the header carrying the tenant identity (`shop-domain`) is outside the signed payload, that same valid `(body, hmac)` pair can be replayed to the app's webhook endpoint with an arbitrary `shop-domain` header value, causing the host application's webhook handler to process attacker-controlled data as if it originated from a different (victim) shop. Depending on what the handler does with `WebhookMetadata#shop` (e.g., looking up/mutating that shop's stored session or data), this is a cross-tenant data-integrity break — the analog of the CCTP bug allowing funds to be routed to an unintended destination because a determinant field escaped validation.

### Likelihood Explanation
Any user can install the app to obtain a validly-signed webhook payload, and the webhook endpoint is a public HTTP endpoint with no additional authentication beyond the HMAC check performed here. Forging the header requires no secret material, only capturing one's own legitimately-signed webhook and reissuing it with a modified `shop-domain` header.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified material, or otherwise cryptographically bind the claimed shop to the request (e.g., verify the shop against a value derived from stored session data associated with the webhook subscription) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture a delivered webhook's raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (valid because `H = HMAC(api_secret_key, B)`).
2. Replay a POST to the app's webhook endpoint with the same body `B`, the same header `H`, but `shopify-shop-domain: victim.myshopify.com` (and desired `shopify-topic`).
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `B` and `H`; `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches to the handler with `shop: "victim.myshopify.com"`, causing the host app to treat attacker-controlled data as an event for the victim shop.

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
