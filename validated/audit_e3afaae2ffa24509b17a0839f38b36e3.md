### Title
Webhook Shop/Topic/ID Fields Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while the `shop`, `topic`, and `webhook_id` fields are read directly from unauthenticated HTTP headers and passed downstream unchecked. `Registry.process` trusts these header-derived values as the tenant identity for dispatching webhook data, even though they are not bound by the HMAC that is verified.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature only over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` returns solely `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to that body or its signature: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` as the authenticated tenant identity for dispatch, without any check that these header values correspond to the shop that actually produced the signed body: [4](#0-3) 

The equality that should hold is: `shop bound by HMAC == shop used to attribute the webhook data`. In this implementation that equality is never enforced — the HMAC only proves "this body was signed with `client_secret`," not "this body belongs to shop X." Since a single app uses one `client_secret` shared across every shop that installs it, an attacker who installs the app on their own (freely obtainable) shop can legitimately receive a genuine `(raw_body, hmac)` pair from Shopify for their own store's events. They can then replay that exact body/hmac pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header to name a victim shop. `HmacValidator.validate` still succeeds (it only checks body vs. signature), and `Registry.process` dispatches the handler with `WebhookMetadata` carrying the attacker-chosen `shop`, `topic`, and `webhook_id` values, causing the host application to process/store data as if it originated from the victim tenant.

### Impact Explanation
This breaks the tenant boundary: an unprivileged internet user (any developer who can install the app on a throwaway shop) can spoof the shop identity attached to a webhook event without ever knowing the app's `client_secret`, injecting attacker-controlled data attributed to an arbitrary victim shop into any app logic keyed off `WebhookMetadata#shop`. This is a cross-tenant access primitive per the Critical impact criteria.

### Likelihood Explanation
Exploitability only requires: (1) the ability to install the target app on any shop (a normal, unprivileged action available to any developer), (2) triggering one webhook event on that shop, and (3) sending an HTTP POST to the app's public webhook endpoint with the captured body/hmac and a forged `shop-domain` header. No secrets, tokens, or privileged access to the victim shop are needed.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the signed material, or cross-check `request.shop` against an independently trusted source (e.g., verify the shop is a currently installed/authorized tenant with an active session) before dispatching to handlers, rather than trusting header values whose integrity is not covered by the HMAC.

### Proof of Concept
1. Install the target Shopify app on an attacker-owned development store (`attacker-shop.myshopify.com`) and register a webhook subscription (e.g. `orders/create`).
2. Trigger the event; capture the resulting POST to the app's webhook endpoint, including `X-Shopify-Hmac-Sha256` header and raw JSON body — both are valid because Shopify signed the body with the app's real `client_secret`.
3. Replay the identical raw body and HMAC header to the same public webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and adjust `X-Shopify-Topic`/`X-Shopify-Webhook-Id` if desired).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC (`lib/shopify_api/webhooks/request.rb` line 37, `lib/shopify_api/utils/hmac_validator.rb` lines 26-31).
5. The handler receives `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` (`lib/shopify_api/webhooks/registry.rb` lines 198-199) with `shop` set to the attacker-chosen `victim-shop.myshopify.com`, causing the host application to process attacker-supplied data under the victim's tenant identity.

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
