### Title
Webhook shop identity spoofing via unauthenticated header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop-domain` (and `topic`, `webhook-id`, `api-version`) values that `ShopifyAPI::Webhooks::Registry.process` hands to application webhook handlers are read straight from unauthenticated HTTP headers. This breaks the identity binding `hmac_valid(body) == shop_that_produced(body)`: any request carrying a previously-obtained valid `(body, hmac)` pair will pass HMAC verification regardless of which shop's domain is asserted in the header.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `Request#shop` (along with `topic`, `api_version`, `webhook_id`) is read directly from headers with no cryptographic tie to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC strictly against `to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` only checks this body HMAC before trusting `request.shop`, `request.topic`, and `request.webhook_id` and forwarding them, unauthenticated, to the app's handler as ground truth for which merchant/topic the payload belongs to: [4](#0-3) 

Because the signature covers only the body, the equality that should hold — "the shop asserted for this payload is the shop Shopify computed the HMAC for" — does not hold. Any party in possession of one legitimately-signed `(body, hmac)` pair (e.g., an attacker who installs the app on their own store and receives a real webhook) can resend that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` still returns `true` (the body/HMAC match), and `Registry.process` will dispatch the handler with `shop:` set to the attacker-chosen value.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as delivered by this gem) to select which tenant's records to update/delete/create from the webhook body — the documented and expected usage pattern — an attacker can make the app apply another merchant's data under a victim shop's identity, or apply their own crafted payload to a victim shop of their choosing. This is a cross-tenant integrity/access issue: the shop-domain binding that applications are expected to rely on for tenant isolation is not authenticated by this library.

### Likelihood Explanation
Exploitation requires only a single legitimately-signed webhook payload, which is trivial to obtain — any merchant (including the attacker, using their own store) can install the app and trigger a real webhook to capture a valid `(raw_body, x-shopify-hmac-sha256)` pair. The attacker then replays that exact body and HMAC to the app's public webhook endpoint with a modified `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header. No access token, `client_secret`, or privileged credential is required — only unprivileged internet access to the app's webhook endpoint.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed material used for verification, or otherwise cryptographically bind them to the body before trusting them (e.g., derive/verify shop identity independently, such as looking up the webhook by `webhook_id` against Shopify's API, or require the caller to supply and verify shop identity out of band rather than trusting the header value forwarded from `Request#shop`).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H`.
2. Attacker sends a new POST to the app's webhook endpoint with the identical body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` computes the HMAC over `B` only (per `Request#to_signable_string`) and succeeds, since `B`/`H` are unchanged. [5](#0-4) 
4. `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from, and was signed for, `attacker-shop.myshopify.com`.

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
