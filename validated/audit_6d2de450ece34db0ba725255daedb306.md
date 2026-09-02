### Title
Webhook shop/topic identity spoofing via HMAC that only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the shop, topic, and webhook-id used to route and attribute the webhook are taken from unauthenticated HTTP headers. `Registry.process` trusts `request.shop` and `request.topic` for dispatch without them being covered by the HMAC that `HmacValidator.validate` checks, so any two deliveries with the same body (including trivial/empty bodies) produce the same valid signature regardless of which shop or topic the headers claim.

### Finding Description
`Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read directly from caller-supplied headers with no cryptographic binding to that body:
```ruby
def topic
  T.cast(shopify_header("topic"), String)
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`Registry.process` validates the HMAC and then dispatches purely on the header-derived `topic`/`shop`, passing them straight into the handler as trusted identity:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

`HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac-sha256` header using `OpenSSL.secure_compare`:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [4](#0-3) 

Because the signable string is only `@raw_body`, the HMAC never binds `shop-domain`, `topic`, or `webhook-id` to the signature. This breaks the intended identity equality: `shop authenticated by HMAC == shop attributed to the delivered event`. Any party who legitimately receives one signed webhook (e.g. an app-installing merchant receiving their own shop's webhooks, such as a low-entropy `{}` body like `app/uninstalled`) can replay that exact `raw_body` + `hmac-sha256` pair to the same public webhook endpoint while substituting an arbitrary `shop-domain` and/or `topic` header. `Registry.process` will accept it as valid and hand the handler a `WebhookMetadata` object claiming to be from a different shop/topic than the one that actually produced the signature.

### Impact Explanation
This is a cross-tenant confusion vector: the app's webhook handler is invoked believing the event originated from shop X (attacker-chosen), when the signature only proves the byte content of the body, not its shop or topic. Depending on how the host app's handler uses `WebhookMetadata#shop` (e.g., to look up/update per-tenant records, deactivate installs, or trigger data mutations keyed by shop), an attacker can forge events attributed to a victim tenant they never had access to. This matches the Critical "cross-tenant access" impact category, since the tenant boundary (`shop`) is not actually bound by the cryptographic proof the library relies on.

### Likelihood Explanation
Exploitation requires the attacker to possess one legitimately signed webhook body/HMAC pair, which is trivial to obtain by installing the app on their own store and capturing any webhook delivery — no secret key, TLS interception, or privileged access is needed. Many webhook topics have fixed, predictable, or empty bodies (e.g., `{}` for several event types), making body/signature reuse across arbitrary `shop`/`topic` header values straightforward.

### Recommendation
Bind the shop and topic identity into the signed material verified before trusting them, or otherwise cryptographically/independently verify that the `shop-domain` and `topic` headers correspond to the shop that installed the app for the given webhook subscription (e.g., cross-check against a known/expected shop for the given webhook `webhook_id`/subscription, or require the host application to independently authenticate the origin shop rather than trusting the header verbatim once the body-only HMAC passes). At minimum, document that `HmacValidator` only authenticates body integrity and that header-derived `shop`/`topic` values must not be treated as authenticated tenant identifiers by consumers of `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a real webhook delivery for a topic with a fixed/empty body, e.g. `app/uninstalled` with body `{}` and a valid `X-Shopify-Hmac-Sha256` header computed over `{}`.
2. Attacker replays this exact body and HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(api_secret_key, "{}")`, unaffected by the header change: [5](#0-4) 
4. The registry looks up the handler by the (attacker-controlled) `topic` and invokes it with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"`, causing the host application's handler logic to act as if the event genuinely originated from the victim shop. [6](#0-5)

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
