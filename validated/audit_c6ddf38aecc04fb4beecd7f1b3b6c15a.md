Confirmed: no additional binding exists anywhere in the gem between `X-Shopify-Shop-Domain` and the HMAC signature. The signature covers only the raw body, so the `shop` value delivered to the app handler is unauthenticated.

### Title
Webhook `shop` (and `topic`/`webhook-id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers, while `to_signable_string` — the value that `Utils::HmacValidator` actually verifies — is only the raw request body. `Registry.process` treats a request as authentic once the body's HMAC checks out, then forwards the header-derived `shop` to the app's webhook handler as the tenant identifier, without that field ever being bound by the signature.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers without any cryptographic tie to the signed content: [2](#0-1) 

`Registry.process` validates only the body HMAC via `Utils::HmacValidator.validate(request)`, then constructs `WebhookMetadata` using the unauthenticated `request.shop`/`request.topic`/`request.webhook_id`, handing that directly to the app's registered handler as the source-of-truth tenant identity: [3](#0-2) 

`HmacValidator.validate_signature` confirms the signature is computed strictly over `verifiable_query.to_signable_string`, i.e. the raw body — never the shop header: [4](#0-3) 

This breaks the intended identity binding `shop_delivered_to_handler == shop_that_the_signature_actually_authenticates`. Since Shopify signs webhooks with the app's shared `client_secret`, and the HMAC only proves "this body was produced using our secret," it says nothing about which shop the body came from. Any entity capable of producing (or replaying) a validly-HMAC'd body — most directly, the malicious developer of their own installed app instance, who legitimately receives real webhooks with a valid HMAC for their own shop — can resend that exact body with a modified `X-Shopify-Shop-Domain` header naming a victim shop. `Utils::HmacValidator.validate` still returns `true` because the body (the only signed field) is untouched, and `Registry.process` will invoke the handler believing the event originated from the victim's tenant.

### Impact Explanation
This is a cross-tenant identity confusion at the point where the gem hands data to the host application: the `shop` value the app uses to route/attribute the event to a merchant record is fully attacker-controlled while claiming a valid signature. Any host application that trusts `WebhookMetadata#shop` (a fully-supported, documented field of this gem) for tenant lookups, without separately re-validating shop ownership, is at risk of writing/reading data under, or triggering business logic for, a different shop's account than the one that actually sent the payload — a cross-tenant access analog to the report's "trusted but unauthenticated field" bug class.

### Likelihood Explanation
Likelihood is High for a merchant/developer who legitimately controls at least one shop with the app installed: they receive real, validly-HMAC'd webhook deliveries for their own shop and can trivially replay the raw body with a forged `shop-domain` header to the app's webhook endpoint (the HMAC computation never inspects any header). No secret material beyond what a legitimate installer already has access to (their own real webhook deliveries) is required.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or independently verify `request.shop` against a value derived from an authenticated source (e.g., cross-check against the session/shop that requested resource, or require the app to look up and verify the reported shop is actually enrolled and match delivery metadata Shopify also embeds in webhook headers meant for this purpose). At minimum, document prominently that `WebhookMetadata#shop` must not be trusted as an authenticated tenant identifier by itself.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a real event (e.g. `orders/create`), receiving a genuine webhook POST with a valid `X-Shopify-Hmac-Sha256` header computed over the raw JSON body using the app's `client_secret`.
2. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into `shop = "victim-shop.myshopify.com"`, `hmac = <unchanged>`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`@raw_body`, unchanged) and returns `true`. [3](#0-2) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes/attributes the event as if it came from the victim, despite the payload actually originating from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
