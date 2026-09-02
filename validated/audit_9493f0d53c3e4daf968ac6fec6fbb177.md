### Title
Webhook shop domain and topic are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator` only authenticates the payload bytes. The `shop-domain`, `topic`, `api-version`, and `webhook-id` headers used by `Webhooks::Registry.process` to dispatch and identify the tenant are read directly from unauthenticated headers and are never bound to the HMAC.

### Finding Description
`Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. `HmacValidator.validate` computes the HMAC exclusively over this signable string: [2](#0-1) 
Meanwhile `Registry.process` trusts `request.shop` and `request.topic` — both parsed straight from HTTP headers — to route and label the webhook without any cross-check against the HMAC-verified content: [3](#0-2) 
And `Request#shop`/`#topic` are plain header reads with no relationship to `hmac`: [4](#0-3) 

This breaks the intended identity binding: `HMAC-verified(raw_body)` should equal `shop-that-the-body-is-attributed-to`, but in this implementation `verified(raw_body) ≠ verified(shop header)`. Anyone who can obtain one legitimate `(raw_body, hmac)` pair from Shopify (e.g., by installing the target app on their own free/test shop and triggering any webhook they control) can replay that exact body and signature to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` and `shopify-topic` header. Because the gem never verifies that the signed body actually originated for that shop/topic, `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop/topic, while carrying attacker-controlled data content that was actually signed for the attacker's own shop.

### Impact Explanation
This is a tenant-identity confusion at the exact boundary the report describes — a field (`shop`, `topic`) that is acted upon by the handler but not covered by the HMAC that is supposed to authenticate the request. Applications typically use `WebhookMetadata#shop` to determine which tenant's records to create/update/delete (e.g., `orders/create`, `app/uninstalled`, `shop/redact`). A forged `shop` header lets an unprivileged caller who controls only their own shop's installation cause the host application to attribute attacker-supplied webhook data to a different, victim shop — a cross-tenant data integrity/confusion issue.

### Likelihood Explanation
Exploitation requires no privileged credentials, no `api_secret_key`, and no TLS interception: an attacker installs the target app on their own store (unprivileged, self-service), triggers any webhook event to obtain one valid `(body, hmac)` pair from Shopify, and replays it directly to the app's public webhook endpoint with forged `shopify-shop-domain`/`shopify-topic` headers. The endpoint is typically internet-reachable by design (that's how Shopify delivers webhooks).

### Recommendation
Bind the identifying headers into the signed material, or otherwise verify them against trusted state before dispatch:
- Reject webhooks where the `shop-domain` header does not match an installation/session already known to the app for that specific correlation (e.g., verify the shop exists in the app's own session store before trusting it), and/or
- Include `topic` and `shop-domain` in the HMAC-signed payload comparison (Shopify does provide the shop and topic in the JSON body for many resources; cross-validate rather than trusting headers alone), and
- Document explicitly that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and must not be used as the sole tenant-selection key without additional verification.

### Proof of Concept
1. Install the target Shopify app on attacker-owned shop `attacker.myshopify.com`.
2. Trigger a webhook (e.g. `carts/update`) and capture the raw POST body `B` and header `x-shopify-hmac-sha256: H` sent by Shopify (valid because it was legitimately signed with the app's real `api_secret_key`).
3. Replay directly to the app's webhook endpoint:
```
POST /webhooks HTTP/1.1
x-shopify-topic: shop/redact
x-shopify-hmac-sha256: H
x-shopify-shop-domain: victim.myshopify.com
x-shopify-webhook-id: <any>
x-shopify-api-version: 2024-01

B
```
4. `HmacValidator.validate` succeeds because it only checks `B` against `H` [5](#0-4) ; `Registry.process` then invokes the registered handler with `shop: "victim.myshopify.com"` and `topic: "shop/redact"` [3](#0-2) , even though the body was never actually signed for that shop or topic.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
